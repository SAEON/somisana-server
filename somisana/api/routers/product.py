from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from starlette.status import HTTP_404_NOT_FOUND

from somisana.api.lib import save_file_resource, delete_local_resource_file
from somisana.api.lib.auth import Authorize
from somisana.api.models import ProductModel, ProductIn, ProductResourceModel, ResourceModel, CatalogProductModel, \
    DatasetModel
from somisana.const import SOMISANAScope, EntityType, ResourceReferenceType, ResourceType
from somisana.db import Session
from somisana.db.models import Product, Resource, ProductResource, ProductVersion

router = APIRouter()


@router.get(
    '/all_products',
    response_model=list[ProductModel],
    dependencies=[Depends(Authorize(SOMISANAScope.PRODUCT_READ))]
)
async def list_products():
    all_products = Session.query(Product).all()

    return [
        output_product_model(product)
        for product in all_products
    ]


@router.get(
    '/catalog_products',
    response_model=list[CatalogProductModel],
    dependencies=[Depends(Authorize(SOMISANAScope.PRODUCT_READ))]
)
async def catalog_products():
    all_products = Session.query(Product).all()

    return [
        catalog_product_model(product)
        for product in all_products
    ]


@router.get(
    '/{product_id}',
    response_model=ProductModel,
    dependencies=[Depends(Authorize(SOMISANAScope.PRODUCT_READ))]
)
async def get_product(
        product_id: int,
) -> ProductModel:
    if not (product := Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return output_product_model(product)


@router.post(
    '/',
    dependencies=[Depends(Authorize(SOMISANAScope.PRODUCT_ADMIN))]
)
async def create_product(
        product_in: ProductIn
) -> int:
    product = Product(
        title=product_in.title,
        description=product_in.description,
        doi=product_in.doi,
        north_bound=product_in.north_bound,
        south_bound=product_in.south_bound,
        east_bound=product_in.east_bound,
        west_bound=product_in.west_bound,
        horizontal_extent=product_in.horizontal_extent,
        horizontal_resolution=product_in.horizontal_resolution,
        vertical_extent=product_in.vertical_extent,
        vertical_resolution=product_in.vertical_resolution,
        temporal_extent=product_in.temporal_extent,
        temporal_resolution=product_in.temporal_resolution,
        variables=product_in.variables,
    )

    product.save()

    if product_in.superseded_product_id:
        ProductVersion(
            product_id=product.id,
            superseded_product_id=product_in.superseded_product_id,
        ).save()

    return product.id


@router.put(
    '/{product_id}',
    dependencies=[Depends(Authorize(SOMISANAScope.PRODUCT_ADMIN))]
)
async def update_product(
        product_id: int,
        product_in: ProductIn
):
    if not (product := Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    product.title = product_in.title,
    product.description = product_in.description,
    product.doi = product_in.doi,
    product.north_bound = product_in.north_bound,
    product.south_bound = product_in.south_bound,
    product.east_bound = product_in.east_bound,
    product.west_bound = product_in.west_bound,
    product.horizontal_extent = product_in.horizontal_extent
    product.horizontal_resolution = product_in.horizontal_resolution
    product.vertical_extent = product_in.vertical_extent
    product.vertical_resolution = product_in.vertical_resolution
    product.temporal_extent = product_in.temporal_extent
    product.temporal_resolution = product_in.temporal_resolution
    product.variables = product_in.variables

    product.save()

    if product_version := Session.get(ProductVersion, product_id):
        if product_in.superseded_product_id:
            product_version.superseded_product_id = product_in.superseded_product_id
            product_version.save()
        else:
            product_version.delete()
    elif product_in.superseded_product_id:
        ProductVersion(
            product_id=product.id,
            superseded_product_id=product_in.superseded_product_id,
        ).save()


@router.delete(
    '/{product_id}',
    dependencies=[Depends(Authorize(SOMISANAScope.PRODUCT_ADMIN))]
)
async def delete_product(
        product_id: int
):
    if not (product := Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    for resource in product.resources:
        if resource.reference_type == ResourceReferenceType.PATH:
            delete_local_resource_file(resource.reference)

    product.delete()


@router.get(
    "/{product_id}/resources/",
    response_model=list[ProductResourceModel],
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_READ))]
)
async def get_resources(
        product_id: int
):
    if not (product := Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return [
        ProductResourceModel(
            id=resource.id,
            product_id=product_id,
            reference=resource.reference,
            resource_type=resource.resource_type,
            reference_type=resource.reference_type,
        ) for resource in product.resources
    ]


@router.post(
    '/{product_id}/resource/',
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_ADMIN))]
)
async def add_resource(
        product_id: int,
        resource_in: ResourceModel,
):
    if not (Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    resource = Resource(
        title=resource_in.title,
        resource_type=resource_in.resource_type,
        reference=resource_in.reference,
        reference_type=ResourceReferenceType.LINK
    )

    resource.save()

    ProductResource(
        product_id=product_id,
        resource_id=resource.id
    ).save()

    return resource.id


@router.put(
    '/{product_id}/resource/',
    dependencies=[Depends(Authorize(SOMISANAScope.RESOURCE_ADMIN))]
)
async def add_file_resource(
        product_id: int,
        resource_query: Annotated[ResourceModel, Query()],
        file: Annotated[UploadFile, File()]
):
    if not (Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    resource_id = save_file_resource(
        file=file,
        resource_model=ResourceModel(**resource_query.dict()),
        entity_type=EntityType.PRODUCT,
        entity_id=product_id
    )

    ProductResource(
        product_id=product_id,
        resource_id=resource_id,
    ).save()

    return resource_id


def output_product_model(product: Product) -> ProductModel:
    return ProductModel(
        id=product.id,
        title=product.title,
        description=product.description,
        doi=product.doi,
        north_bound=product.north_bound,
        south_bound=product.south_bound,
        east_bound=product.east_bound,
        west_bound=product.west_bound,
        horizontal_extent=product.horizontal_extent,
        horizontal_resolution=product.horizontal_resolution,
        vertical_extent=product.vertical_extent,
        vertical_resolution=product.vertical_resolution,
        temporal_extent=product.temporal_extent,
        temporal_resolution=product.temporal_resolution,
        variables=product.variables,
        superseded_product_id=product.supersedes.superseded_product_id if product.supersedes else None,
        datasets=[
            DatasetModel(
                id=dataset.id,
                product_id=dataset.product_id,
                title=dataset.title,
                folder_path=dataset.folder_path,
                data_access_urls=(
                    ResourceModel(
                        id=resource.id,
                        title=resource.title,
                        reference=resource.reference,
                        resource_type=resource.resource_type,
                        reference_type=resource.reference_type
                    )
                    for resource in dataset.resources
                    if resource.resource_type == ResourceType.DATA_ACCESS_URL
                ),
                cover_image=get_first_resource(dataset.resources, ResourceType.COVER_IMAGE)
            )
            for dataset in product.datasets
        ],
        resources=[
            ResourceModel(
                id=resource.id,
                title=resource.title,
                reference=resource.reference,
                resource_type=resource.resource_type,
                reference_type=resource.reference_type,
            )
            for resource in product.resources
        ]
    )


def catalog_product_model(product: Product) -> CatalogProductModel:
    return CatalogProductModel(
        id=product.id,
        title=product.title,
        description=product.description,
        thumbnail=get_first_resource(product.resources, ResourceType.THUMBNAIL)
    )


def get_first_resource(resources: list[Resource], resource_type: ResourceType) -> ResourceModel:
    return next(
        (
            ResourceModel(
                id=resource.id,
                title=resource.title,
                reference=resource.reference,
                resource_type=resource_type,
                reference_type=resource.reference_type,
            )
            for resource in resources
            if resource.resource_type == resource_type
        ),
        None
    )
