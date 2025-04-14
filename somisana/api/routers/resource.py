import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, UploadFile, HTTPException, Query, File, Depends
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from somisana.api.lib.auth import Authorize
from somisana.api.models import ResourceModel
from somisana.const import ResourceType, ResourceReferenceType
from somisana.const import SOMISANAScope
from somisana.db import Session
from somisana.db.models import Product, Resource

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
        product_id=resource.product_id,
        resource_type=resource.resource_type,
        reference_type=resource.reference_type,
    )


@router.get(
    "/product_resources/{product_id}",
    response_model=list[ResourceModel],
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_READ))]
)
async def get_product_resources(
        product_id: int
):
    stmt = select(Resource).where(Resource.product_id == product_id)
    resources = Session.execute(stmt).scalars().all()

    return [
        ResourceModel(
            id=resource.id,
            product_id=resource.product_id,
            reference=resource.reference,
            resource_type=resource.resource_type,
            reference_type=resource.reference_type,
        ) for resource in resources
    ]


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


@router.put(
    '/',
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_ADMIN))]
)
async def add_file_resource(
        resource_query: Annotated[ResourceModel, Query()],
        file: Annotated[UploadFile, File()]
):
    if not (Session.get(Product, resource_query.product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    file_path = save_local_resource_file(resource_query.product_id, file)

    resource = Resource(
        product_id=resource_query.product_id,
        resource_type=resource_query.resource_type,
        reference=file_path,
        reference_type=ResourceReferenceType.PATH
    )

    resource.save()


@router.post(
    '/',
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_ADMIN))]
)
async def add_resource(
        resource_in: ResourceModel
):
    if not (Session.get(Product, resource_in.product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    resource = Resource(
        product_id=resource_in.product_id,
        resource_type=resource_in.resource_type,
        reference=resource_in.reference,
        reference_type=ResourceReferenceType.LINK
    )

    resource.save()

    return resource.id


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


def save_local_resource_file(product_id: int, local_file: UploadFile) -> str:
    product_local_resource_dir = f"{Path.home()}/somisana/resources/{product_id}"

    if not os.path.exists(product_local_resource_dir):
        os.makedirs(product_local_resource_dir)

    file_path = f"{product_local_resource_dir}/{local_file.filename}"

    with open(file_path, "wb") as f:
        f.write(local_file.file.read())

    return file_path


def delete_local_resource_file(resource_path):
    if os.path.exists(resource_path):
        os.remove(resource_path)
