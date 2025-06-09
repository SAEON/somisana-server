from sqlalchemy import select

from somisana.db.models import (
    Product,
    Resource
)
from test import TestSession
from .factories import (
    ProductFactory, ProductResourceFactory,
    DatasetFactory, ResourceFactory, DatasetResourceFactory,
    ProductVersionFactory
)


def test_product():
    old_product = ProductFactory()
    product = ProductFactory()

    ProductVersionFactory(product=product, superseded_product=old_product)

    resource_1 = ResourceFactory()
    resource_2 = ResourceFactory()

    ProductResourceFactory(product=product, resource=resource_1)
    ProductResourceFactory(product=product, resource=resource_2)

    dataset_1 = DatasetFactory(product=product)
    dataset_2 = DatasetFactory(product=product)

    resource_3 = ResourceFactory()
    resource_4 = ResourceFactory()

    DatasetResourceFactory(dataset=dataset_1, resource=resource_3)
    DatasetResourceFactory(dataset=dataset_2, resource=resource_4)

    result = TestSession.get(Product, product.id)

    compare_products(product, result)


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
               product1.west_bound,
               product1.horizontal_resolution,
               product1.vertical_extent,
               product1.vertical_resolution,
               product1.temporal_extent,
               product1.temporal_resolution,
               product1.variables
           ) == (
               product2.id,
               product2.title,
               product2.description,
               product2.doi,
               product2.north_bound,
               product2.south_bound,
               product2.east_bound,
               product2.west_bound,
               product2.horizontal_resolution,
               product2.vertical_extent,
               product2.vertical_resolution,
               product2.temporal_extent,
               product2.temporal_resolution,
               product2.variables
           )

    for dataset in product1.datasets:
        matching_dataset = next((d for d in product2.datasets if d.id == dataset.id), None)
        assert matching_dataset is not None
        compare_datasets(dataset, matching_dataset)

    for resource in product1.resources:
        matching_resource = next((r for r in product2.resources if r.id == resource.id), None)
        assert matching_resource is not None
        compare_resources(resource, matching_resource)


def compare_datasets(dataset1, dataset2):
    assert (
               dataset1.id,
               dataset1.product_id,
               dataset1.title,
               dataset1.folder_path
           ) == (
               dataset2.id,
               dataset2.product_id,
               dataset2.title,
               dataset2.folder_path
           )

    for resource in dataset1.resources:
        matching_resource = next((r for r in dataset2.resources if r.id == resource.id), None)
        assert matching_resource is not None
        compare_resources(resource, matching_resource)


def compare_resources(resource1, resource2):
    assert (
               resource1.id,
               resource1.title,
               resource1.reference,
               resource1.reference_type,
               resource1.resource_type
           ) == (
               resource2.id,
               resource2.title,
               resource2.reference,
               resource2.reference_type,
               resource2.resource_type
           )
