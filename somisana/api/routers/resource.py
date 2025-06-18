from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from somisana.api.lib import delete_local_resource_file
from somisana.api.lib.auth import Authorize
from somisana.api.models import ResourceModel
from somisana.const import ResourceType, ResourceReferenceType
from somisana.const import SOMISANAScope
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
