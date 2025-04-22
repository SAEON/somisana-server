from typing import Annotated

from fastapi import APIRouter, UploadFile, HTTPException, Query, File, Depends
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from somisana.api.lib import save_file_resource, delete_local_resource_file
from somisana.api.lib.auth import Authorize
from somisana.api.models import ResourceModel, ProductResourceModel, SimulationResourceModel
from somisana.const import ResourceType, ResourceReferenceType
from somisana.const import SOMISANAScope, EntityType
from somisana.db import Session
from somisana.db.models import Product, Resource, Simulation, ProductResource, SimulationResource

router = APIRouter()


@router.get(
    "/{resource_id}",
    response_model=ResourceModel,
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_READ))]
)
async def get_resource(
        resource_id: int
):
    if not (resource := Session.get(Resource, resource_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return ResourceModel(
        id=resource.id,
        reference=resource.reference,
        resource_type=resource.resource_type,
        reference_type=resource.reference_type,
    )


@router.get(
    "/{product_id}/{resource_type}",
    response_model=list[ResourceModel],
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_READ))]
)
async def get_resources_by_resource_type(
        product_id: int,
        resource_type: ResourceType
):
    stmt = (
        select(Resource)
        .where(Resource.product_id == product_id)
        .where(Resource.resource_type == resource_type)
    )

    return [
        ResourceModel(
            reference=resource.reference,
            resource_type=resource.resource_type,
            reference_type=resource.reference_type,
        ) for resource in Session.execute(stmt).scalars().all()
    ]


@router.delete(
    '/{resource_id}',
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_ADMIN))]
)
async def delete_resource(
        resource_id: int
):
    if not (resource := Session.get(Resource, resource_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if resource.reference == ResourceReferenceType.PATH:
        delete_local_resource_file(resource.reference)

    resource.delete()
