from somisana.db.models import Product
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


def compare_products(product_1, product_2):
    assert (product_1.to_dict() == product_2.to_dict())

    for dataset in product_1.datasets:
        matching_dataset = next((d for d in product_2.datasets if d.id == dataset.id), None)
        assert matching_dataset is not None
        compare_datasets(dataset, matching_dataset)

    for resource in product_1.resources:
        matching_resource = next((r for r in product_2.resources if r.id == resource.id), None)
        assert matching_resource is not None
        assert (resource.to_dict() == matching_resource.to_dict())


def compare_datasets(dataset_1, dataset_2):
    assert (dataset_1.to_dict() == dataset_2.to_dict())

    for resource in dataset_1.resources:
        matching_resource = next((r for r in dataset_2.resources if r.id == resource.id), None)
        assert matching_resource is not None
        assert (resource.to_dict() == matching_resource.to_dict())

