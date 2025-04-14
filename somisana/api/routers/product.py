from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from starlette.status import HTTP_404_NOT_FOUND

from somisana.api.lib.auth import Authorize
from somisana.api.models import ProductModel, ProductIn, SimulationModel
from somisana.const import ResourceReferenceType
from somisana.const import SOMISANAScope
from somisana.db import Session
from somisana.db.models import Product, Simulation, Resource
from .resource import delete_local_resource_file

router = APIRouter()


@router.get(
    '/all_products',
    dependencies=[Depends(Authorize(SOMISANAScope.PRODUCT_READ))]
)
async def list_products():
    all_products = Session.query(Product).all()

    return all_products


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
        simulations=[
            SimulationModel(
                id=simulation.id,
                title=simulation.title,
                folder_path=simulation.folder_path,
                data_access_url=simulation.data_access_url
            )
            for simulation in product.simulations
        ]
    )


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
        simulations=[
            Session.get(Simulation, simulation_id)
            for simulation_id in product_in.simulation_ids
        ]
    )

    product.save()

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
    product.simulations = [
        Session.get(Simulation, simulation_id)
        for simulation_id in product_in.simulation_ids
    ]

    product.save()


@router.delete(
    '/{product_id}',
    dependencies=[Depends(Authorize(SOMISANAScope.PRODUCT_ADMIN))]
)
async def delete_product(
        product_id: int
):
    if not (product := Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    stmt = (
        select(Resource)
        .where(Resource.product_id == product_id)
        .where(Resource.reference_type == ResourceReferenceType.PATH)
    )

    resources = Session.execute(stmt).scalars().all()

    for resource in resources:
        delete_local_resource_file(resource.reference)

    product.delete()
