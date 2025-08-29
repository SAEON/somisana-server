from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from somisana.api.lib import save_file_resource, delete_local_resource_file, update_file_resource
from typing import Annotated
from starlette.status import HTTP_404_NOT_FOUND

from somisana.api.lib import delete_local_resource_file
from somisana.api.lib.auth import Authorize
from somisana.api.models import ResourceModel
from somisana.const import ResourceReferenceType, EntityType, SOMISANAScope
from somisana.db import Session
from somisana.db.models import Resource

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
        title=resource.title,
        reference=resource.reference,
        resource_type=resource.resource_type,
        reference_type=resource.reference_type,
    )


@router.delete(
    '/{resource_id}',
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_ADMIN))]
)
async def delete_resource(
        resource_id: int
):
    if not (resource := Session.get(Resource, resource_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    if resource.reference_type == ResourceReferenceType.PATH:
        delete_local_resource_file(resource.reference)

    resource.delete()


@router.post(
    '/{resource_id}/',
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_ADMIN))]
)
async def update_resource(
        resource_id: int,
        resource_in: ResourceModel,
):
    if not (resource := Session.get(Resource, resource_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    resource.title = resource_in.title,
    resource.resource_type = resource_in.resource_type,
    resource.reference = resource_in.reference,

    resource.save()

    return resource.id


@router.put(
    '/{resource_id}/',
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_ADMIN))]
)
async def update_resource_file(
        resource_id: int,
        resource_query: Annotated[ResourceModel, Query()],
        file: Annotated[UploadFile, File()]
):
    if not (resource := Session.get(Resource, resource_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    entity_type = ''
    entity_id = 0

    if resource.products:
        entity_type = EntityType.PRODUCT.value
        entity_id = resource.products[0].id
    elif resource.datasets:
        entity_type = EntityType.DATASET.value
        entity_id = resource.datasets[0].id

    resource_model = ResourceModel(**resource_query.dict())
    resource.title = resource_model.title,
    resource.resource_type = resource_model.resource_type,

    update_file_resource(file, resource, entity_type, entity_id)

    return resource_id
