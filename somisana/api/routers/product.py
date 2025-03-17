import os
from pathlib import Path

from fastapi import APIRouter, UploadFile, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

from somisana.api.models import ProductIn, ProductModel, SimulationModel
from somisana.db import Session
from somisana.db.models import Product, Simulation

router = APIRouter()


@router.get(
    '/all_products'
)
async def list_products():
    all_products = Session.query(Product).all()

    return all_products


@router.get(
    '/{product_id}'
)
async def get_product(
        product_id: int
) -> ProductModel:
    if not (product := Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    return output_product_model(product)


def output_product_model(product: Product) -> ProductModel:
    return ProductModel(
        id=product.id,
        title=product.title,
        abstract=product.abstract,
        doi=product.doi,
        north_bound=product.north_bound,
        south_bound=product.south_bound,
        east_bound=product.east_bound,
        west_bound=product.west_bound,
        simulations=[
            SimulationModel(
                id=simulation.id,
                folder_path=simulation.folder_path,
                data_access_url=simulation.data_access_url
            )
            for simulation in product.simulations
        ]
    )


@router.post(
    '/'
)
async def create_product(
        product_in: ProductIn
) -> int:
    product = Product(
        title=product_in.title,
        abstract=product_in.abstract,
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


@router.post(
    '/cover_image/{product_id}'
)
async def set_product_cover_image(
        product_id: int,
        cover_image: UploadFile
):
    if not (product := Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    cover_images_dir = f"{Path.home()}/somisana/cover_images"

    if not os.path.exists(cover_images_dir):
        os.makedirs(cover_images_dir)

    file_path = f"{cover_images_dir}/{cover_image.filename}"

    with open(file_path, "wb") as f:
        f.write(cover_image.file.read())

    if product.cover_image_path:
        delete_cover_image_file(product.cover_image_path)

    product.cover_image_path = file_path
    product.save()


@router.put(
    '/{product_id}'
)
async def update_product(
        product_id: int,
        product_in: ProductIn
):
    if not (product := Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    product.title = product_in.title,
    product.abstract = product_in.abstract,
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
    '/{product_id}'
)
async def delete_product(
        product_id: int
):
    if not (product := Session.get(Product, product_id)):
        raise HTTPException(HTTP_404_NOT_FOUND)

    delete_cover_image_file(product.cover_image_path)

    product.delete()


def delete_cover_image_file(cover_image_path):
    if os.path.exists(cover_image_path):
        os.remove(cover_image_path)
