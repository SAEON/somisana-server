from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from starlette.status import HTTP_404_NOT_FOUND

from somisana.api.lib import save_file_resource, delete_local_resource_file
from somisana.api.lib.auth import Authorize
from somisana.api.models import DatasetModel, ResourceModel, DatasetInModel
from somisana.const import SOMISANAScope, EntityType, ResourceType, ResourceReferenceType
from somisana.db import Session
from somisana.db.models import Dataset, DatasetResource, Resource

router = APIRouter()


@router.get(
    '/all',
    dependencies=[Depends(Authorize(SOMISANAScope.DATASET_READ))]
)
async def list_datasets():
    all_datasets = Session.query(Dataset).all()

    return all_datasets


@router.get(
    '/{dataset_id}',
    response_model=DatasetModel,
    dependencies=[Depends(Authorize(SOMISANAScope.DATASET_READ))]
)
async def get_dataset(
        dataset_id: int,
) -> DatasetModel:
    if not (dataset := Session.get(Dataset, dataset_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return DatasetModel(
        id=dataset.id,
        product_id=dataset.product_id,
        title=dataset.title,
        folder_path=dataset.folder_path,
        data_access_urls=[
            ResourceModel(
                id=resource.id,
                title=resource.title,
                reference=resource.reference,
                resource_type=resource.resource_type,
                reference_type=resource.reference_type
            )
            for resource in dataset.resources
            if resource.resource_type == ResourceType.DATA_ACCESS_URL
        ],
        cover_image=next(
            (
                ResourceModel(
                    id=resource.id,
                    title=resource.title,
                    reference=resource.reference,
                    resource_type=resource.resource_type,
                    reference_type=resource.reference_type
                )
                for resource in dataset.resources
                if resource.resource_type == ResourceType.COVER_IMAGE
            ),
            None
        ),
    )


@router.post(
    '/',
    dependencies=[Depends(Authorize(SOMISANAScope.DATASET_ADMIN))]
)
async def create_dataset(
        dataset_in: DatasetInModel
) -> int:
    dataset = Dataset(
        product_id=dataset_in.product_id,
        title=dataset_in.title,
        folder_path=dataset_in.folder_path
    )

    dataset.save()

    return dataset.id


@router.put(
    '/{dataset_id}',
    dependencies=[Depends(Authorize(SOMISANAScope.DATASET_ADMIN))]
)
async def update_dataset(
        dataset_id: int,
        dataset_in: DatasetInModel
):
    if not (dataset := Session.get(Dataset, dataset_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    dataset.product_id = dataset_in.product_id,
    dataset.title = dataset_in.title,
    dataset.folder_path = dataset_in.folder_path,

    dataset.save()


@router.delete(
    '/{dataset_id}',
    dependencies=[Depends(Authorize(SOMISANAScope.DATASET_ADMIN))]
)
async def delete_dataset(
        dataset_id: int
):
    if not (dataset := Session.get(Dataset, dataset_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    # First delete all uploaded files for that dataset
    for resource in dataset.resources:
        if resource.reference_type == ResourceReferenceType.PATH:
            delete_local_resource_file(resource.reference)

    dataset.delete()


@router.post(
    '/{dataset_id}/resource/',
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_ADMIN))]
)
async def add_resource(
        dataset_id: int,
        resource_in: ResourceModel,
):
    if not (Session.get(Dataset, dataset_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    resource = Resource(
        title=resource_in.title,
        resource_type=resource_in.resource_type,
        reference=resource_in.reference,
        reference_type=ResourceReferenceType.LINK
    )

    resource.save()

    DatasetResource(
        dataset_id=dataset_id,
        resource_id=resource.id
    ).save()

    return resource.id


@router.put(
    '/{dataset_id}/resource/',
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_ADMIN))]
)
async def add_file_resource(
        dataset_id: int,
        resource_query: Annotated[ResourceModel, Query()],
        file: Annotated[UploadFile, File()]
):
    if not (Session.get(Dataset, dataset_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    resource_id = save_file_resource(
        file=file,
        resource_model=ResourceModel(**resource_query.dict()),
        entity_type=EntityType.DATASET,
        entity_id=dataset_id,
    )

    DatasetResource(
        dataset_id=dataset_id,
        resource_id=resource_id,
    ).save()

    return resource_id
