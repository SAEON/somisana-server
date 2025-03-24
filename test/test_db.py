from .factories import (
    ProductFactory,
    SimulationFactory, ResourceFactory
)
from sqlalchemy import select

from somisana.db.models import (
    Product,
    Simulation,
    Resource
)
from test import TestSession


def test_product():
    product = ProductFactory()
    result = TestSession.execute(select(Product)).scalar()

    compare_products(product, result)


def test_simulation():
    simulation = SimulationFactory()
    result = TestSession.execute(select(Simulation)).scalar()

    assert (
               result.id,
               result.folder_path,
               result.data_access_url,
           ) == (
               simulation.id,
               simulation.folder_path,
               simulation.data_access_url,
           )


def test_product_with_simulations():
    simulation1 = SimulationFactory()
    simulation2 = SimulationFactory()

    product = ProductFactory(simulations=[simulation1, simulation2])

    result = TestSession.execute(select(Product)).scalar()

    compare_products(product, result)

    for index, simulation in enumerate(result.simulations):
        compare_simulations(simulation, [simulation1, simulation2][index])


def test_resource():
    resource = ResourceFactory()

    result = TestSession.execute(select(Resource)).scalar()

    compare_resources(resource, result)


def test_product_with_resources():
    product = ProductFactory()

    resource1 = ResourceFactory(product=product)
    resource2 = ResourceFactory(product=product)

    result = TestSession.execute(select(Product)).scalar()

    compare_products(product, result)

    for index, resource in enumerate(result.resources):
        compare_resources(resource, [resource1, resource2][index])


def compare_products(product1, product2):
    assert (
               product1.id,
               product1.title,
               product1.description,
               product1.doi,
               product1.north_bound,
               product1.south_bound,
               product1.east_bound,
               product1.west_bound
           ) == (
               product2.id,
               product2.title,
               product2.description,
               product2.doi,
               product2.north_bound,
               product2.south_bound,
               product2.east_bound,
               product2.west_bound
           )


def compare_simulations(simulation1, simulation2):
    assert (
               simulation1.id,
               simulation1.folder_path,
               simulation1.data_access_url,
           ) == (
               simulation2.id,
               simulation2.folder_path,
               simulation2.data_access_url,
           )


def compare_resources(resource1, resource2):
    assert (
        resource1.id,
        resource1.product_id,
        resource1.reference,
        resource1.reference_type,
        resource1.resource_type,
    ) == (
        resource2.id,
        resource2.product_id,
        resource2.reference,
        resource2.reference_type,
        resource2.resource_type,
    )