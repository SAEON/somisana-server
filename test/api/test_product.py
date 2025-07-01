from decimal import Decimal

import pytest

from somisana.const import SOMISANAScope, ResourceType
from somisana.db.models import Product
from test import TestSession
from test.api import assert_forbidden
from test.factories import ProductFactory, DatasetFactory, ResourceFactory, ProductVersionFactory, \
    DatasetResourceFactory, ProductResourceFactory


@pytest.mark.require_scope(SOMISANAScope.PRODUCT_READ)
def test_get_catalog_products(api, scopes):
    authorized = SOMISANAScope.PRODUCT_READ in scopes

    batch_size = 5
    product_batch = ProductFactory.create_batch(batch_size)
    # Add an entry so that product 0 supersedes product 1
    superseded_product = product_batch[1]
    ProductVersionFactory(product=product_batch[0], superseded_product=superseded_product)

    r = api(scopes).get('/product/catalog_products/')

    if not authorized:
        assert_forbidden(r)
    else:
        catalog_products = r.json()
        # The superseded product should not be returned to the catalog
        assert len(catalog_products) == batch_size - 1
        assert all(product['id'] != superseded_product.id for product in catalog_products)


@pytest.mark.require_scope(SOMISANAScope.PRODUCT_READ)
def test_get_product(api, scopes):
    authorized = SOMISANAScope.PRODUCT_READ in scopes

    product = ProductFactory.create()

    superseded_product = ProductFactory.create()
    ProductVersionFactory.create(product=product, superseded_product=superseded_product)

    dataset = DatasetFactory.create(product=product)

    dataset_data_access_url = ResourceFactory.create(resource_type=ResourceType.DATA_ACCESS_URL)
    DatasetResourceFactory.create(dataset=dataset, resource=dataset_data_access_url)

    dataset_cover_image = ResourceFactory.create(resource_type=ResourceType.COVER_IMAGE)
    DatasetResourceFactory.create(dataset=dataset, resource=dataset_cover_image)

    product_thumbnail = ResourceFactory.create(resource_type=ResourceType.THUMBNAIL)
    ProductResourceFactory.create(product=product, resource=product_thumbnail)

    r = api(scopes).get(f'/product/{product.id}/')

    if not authorized:
        assert_forbidden(r)
    else:
        fetched_product = r.json()
        compare_products(product, fetched_product)
        assert fetched_product['superseded_product_id'] == superseded_product.id

        fetched_dataset = fetched_product['datasets'][0]
        compare_datasets(dataset, fetched_dataset)

        compare_resources(dataset_data_access_url, fetched_dataset['data_access_urls'][0])
        compare_resources(dataset_cover_image, fetched_dataset['cover_image'])

        compare_resources(product_thumbnail, fetched_product['resources'][0])


@pytest.mark.require_scope(SOMISANAScope.PRODUCT_ADMIN)
def test_add_product(api, scopes):
    authorized = SOMISANAScope.PRODUCT_ADMIN in scopes

    product = ProductFactory.build()

    r = api(scopes).post('/product/', json=dict(
        title=product.title,
        description=product.description,
        doi=product.doi,
        north_bound=str(product.north_bound),
        south_bound=str(product.south_bound),
        east_bound=str(product.east_bound),
        west_bound=str(product.west_bound),
        horizontal_resolution=product.horizontal_resolution,
        vertical_extent=product.vertical_extent,
        vertical_resolution=product.vertical_resolution,
        temporal_extent=product.temporal_extent,
        temporal_resolution=product.temporal_resolution,
        variables=product.variables,
    ))

    if not authorized:
        assert_forbidden(r)
    else:
        new_product_id = r.json()

        fetched_product: Product = TestSession.get(Product, new_product_id)

        # Set the built factories' id to the fetched products' id to compare them
        product.id = fetched_product.id

        assert (fetched_product.to_dict() == product.to_dict())


@pytest.mark.require_scope(SOMISANAScope.PRODUCT_ADMIN)
def test_update_product(api, scopes):
    authorized = SOMISANAScope.PRODUCT_ADMIN in scopes

    product = ProductFactory.create()

    updated_product = ProductFactory.build()

    # Make sure they are not the same
    assert (product.to_dict() != updated_product.to_dict())

    r = api(scopes).put(f'/product/{product.id}', json=dict(
        title=updated_product.title,
        description=updated_product.description,
        doi=updated_product.doi,
        north_bound=str(updated_product.north_bound),
        south_bound=str(updated_product.south_bound),
        east_bound=str(updated_product.east_bound),
        west_bound=str(updated_product.west_bound),
        horizontal_resolution=updated_product.horizontal_resolution,
        vertical_extent=updated_product.vertical_extent,
        vertical_resolution=updated_product.vertical_resolution,
        temporal_extent=updated_product.temporal_extent,
        temporal_resolution=updated_product.temporal_resolution,
        variables=updated_product.variables,
    ))

    if not authorized:
        assert_forbidden(r)
    else:
        fetched_product = TestSession.get(Product, product.id)

        # Set the built factories' id to the fetched products' id to compare them
        updated_product.id = fetched_product.id

        assert (fetched_product.to_dict() == updated_product.to_dict())


@pytest.mark.require_scope(SOMISANAScope.PRODUCT_ADMIN)
def test_delete_product(api, scopes):
    authorized = SOMISANAScope.PRODUCT_ADMIN in scopes

    product = ProductFactory.create()

    r = api(scopes).delete(f'/product/{product.id}')

    if not authorized:
        assert_forbidden(r)
    else:
        assert TestSession.get(Product, product.id) is None


@pytest.mark.require_scope(SOMISANAScope.RESOURCE_READ)
def test_get_resources(api, scopes):
    authorized = SOMISANAScope.RESOURCE_READ in scopes

    resource1 = ResourceFactory.create()
    resource2 = ResourceFactory.create()

    product = ProductFactory.create()

    ProductVersionFactory.create(product=product, resource=resource1)
    ProductVersionFactory.create(product=product, resource=resource2)

    r = api(scopes).get(f'/product/{product.id}/resources')

    if not authorized:
        assert_forbidden(r)
    else:
        for resource in r.json():
            if resource['id'] == resource1.id:
                compare_resources(resource1, resource)
            else:
                compare_resources(resource2, resource)


def compare_products(product, product_json):
    assert (
               product.id,
               product.title,
               product.description,
               product.doi,
               float(product.north_bound),
               float(product.south_bound),
               float(product.east_bound),
               float(product.west_bound),
               product.horizontal_resolution,
               product.vertical_extent,
               product.vertical_resolution,
               product.temporal_extent,
               product.temporal_resolution,
               product.variables,
           ) == (
               product_json['id'],
               product_json['title'],
               product_json['description'],
               product_json['doi'],
               product_json['north_bound'],
               product_json['south_bound'],
               product_json['east_bound'],
               product_json['west_bound'],
               product_json['horizontal_resolution'],
               product_json['vertical_extent'],
               product_json['vertical_resolution'],
               product_json['temporal_extent'],
               product_json['temporal_resolution'],
               product_json['variables']
           )


def compare_datasets(dataset, dataset_json):
    assert (
               int(dataset.id),
               dataset.product_id,
               dataset.title,
               dataset.folder_path
           ) == (
               int(dataset_json['id']),
               dataset_json['product_id'],
               dataset_json['title'],
               dataset_json['folder_path']
           )


def compare_resources(resource, resource_json):
    assert (
               int(resource.id),
               resource.title,
               resource.reference,
               resource.resource_type,
               resource.reference_type
           ) == (
               int(resource_json['id']),
               resource_json['title'],
               resource_json['reference'],
               resource_json['resource_type'],
               resource_json['reference_type']
           )
