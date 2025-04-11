import os
from pathlib import Path

from typing import Annotated

from fastapi import APIRouter, UploadFile, HTTPException, Form, File
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
    response_model=list[ResourceModel]
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
    '/file'
)
async def add_file_resource(
        resource_type: Annotated[ResourceType, Form()],
        product_id: Annotated[int, Form()],
        file: Annotated[UploadFile, File()]
):
    if not (Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    file_path = save_local_resource_file(product_id, file)

    resource = Resource(
        product_id=product_id,
        resource_type=resource_type,
        reference=file_path,
        reference_type=ResourceReferenceType.PATH
    )

    resource.save()


@router.post(
    '/'
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


@router.put(
    '/file/{resource_id}'
)
async def update_file_resource(
        resource_id: int,
        resource_type: Annotated[ResourceType, Form()],
        product_id: Annotated[int, Form()],
        file: Annotated[UploadFile, File()]
):
    if not (resource := Session.get(Resource, resource_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    file_path = save_local_resource_file(product_id, file)

    delete_local_resource_file(resource.reference)

    resource.resource_type = resource_type
    resource.reference = file_path
    resource.reference_type = ResourceReferenceType.PATH
    resource.save()


@router.put(
    '/{resource_id}'
)
async def update_resource(
        resource_id: int,
        resource_in: ResourceModel
):
    if not (resource := Session.get(Resource, resource_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    resource.resource_type = resource_in.resource_type
    resource.reference = resource_in.reference
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
