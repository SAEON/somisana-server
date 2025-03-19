import os
from pathlib import Path

from fastapi import APIRouter, UploadFile, HTTPException
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from somisana.const import ResourceType, ResourceReferenceType
from somisana.db import Session
from somisana.db.models import Product, Resource
from somisana.api.models import ResourceModel

router = APIRouter()


@router.get(
    "/{resource_id}",
    response_model=ResourceModel
)
async def get_resource_by_id(
        resource_id: int
):
    if not (resource := Session.get(Resource, resource_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return ResourceModel(
        reference=resource.reference,
        resource_type=resource.resource_type,
        reference_type=resource.reference_type,
    )


@router.get(
    "/{product_id}/{resource_type}",
    response_model=list[ResourceModel]
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


@router.post(
    '/local/{resource_type}/{product_id}'
)
async def add_local_resource(
        resource_type: ResourceType,
        product_id: int,
        local_file: UploadFile
):
    if not (Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    file_path = save_local_resource_file(product_id, local_file)

    resource = Resource(
        product_id=product_id,
        resource_type=resource_type,
        reference=file_path,
        reference_type=ResourceReferenceType.PATH
    )

    resource.save()


@router.post(
    '/{resource_type}/{product_id}'
)
async def add_resource(
        resource_type: ResourceType,
        product_id: int,
        reference: str
):
    if not (Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    resource = Resource(
        product_id=product_id,
        resource_type=resource_type,
        reference=reference,
        reference_type=ResourceReferenceType.LINK
    )

    resource.save()


@router.put(
    '/local/{resource_type}/{resource_id}'
)
async def update_local_resource(
        resource_type: ResourceType,
        resource_id: int,
        local_file: UploadFile
):
    if not (resource := Session.get(Resource, resource_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    file_path = save_local_resource_file(resource_id.product_id, local_file)

    delete_local_resource_file(resource.reference)

    resource.resource_type = resource_type
    resource.reference = file_path
    resource.reference_type = ResourceReferenceType.PATH
    resource.save()


@router.put(
    '/{resource_type}/{resource_id}'
)
async def update_resource(
        resource_type: ResourceType,
        resource_id: int,
        reference: str
):
    if not (resource := Session.get(Resource, resource_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    resource.resource_type = resource_type
    resource.reference = reference
    resource.reference_type = ResourceReferenceType.LINK
    resource.save()


@router.delete(
    '/{resource_id}'
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
