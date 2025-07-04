import filecmp
import shutil
from pathlib import Path

import pytest

from somisana.api.lib import local_resource_folder_path
from somisana.const import SOMISANAScope, ResourceType, ResourceReferenceType
from somisana.db.models import Product, Resource
from test import TestSession
from test.api import assert_forbidden
from test.api.lib import compare_datasets, compare_resources, compare_products
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

        created_product: Product = TestSession.get(Product, new_product_id)

        # Set the built factories' id to the created products' id to compare them
        product.id = created_product.id

        assert (created_product.to_dict() == product.to_dict())


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
        created_product = TestSession.get(Product, product.id)

        # Set the built factories' id to the created products' id to compare them
        updated_product.id = created_product.id

        assert (created_product.to_dict() == updated_product.to_dict())


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

    ProductResourceFactory.create(product=product, resource=resource1)
    ProductResourceFactory.create(product=product, resource=resource2)

    r = api(scopes).get(f'/product/{product.id}/resources')

    if not authorized:
        assert_forbidden(r)
    else:
        for resource in r.json():
            if int(resource['id']) == resource1.id:
                compare_resources(resource1, resource)
            else:
                compare_resources(resource2, resource)


@pytest.mark.require_scope(SOMISANAScope.RESOURCE_ADMIN)
def test_add_resource(api, scopes):
    authorized = SOMISANAScope.RESOURCE_ADMIN in scopes

    product = ProductFactory.create()

    # Set the reference typ because only links are added via this route
    resource = ResourceFactory.build(reference_type=ResourceReferenceType.LINK)

    r = api(scopes).post(f'/product/{product.id}/resource/', json=dict(
        title=resource.title,
        resource_type=resource.resource_type,
        reference=resource.reference
    ))

    if not authorized:
        assert_forbidden(r)
    else:
        new_resource_id = r.json()

        # Set the factory resource id so they can be compared
        resource.id = new_resource_id

        created_resource = TestSession.get(Resource, new_resource_id)

        compare_resources(created_resource, resource.to_dict())


@pytest.mark.require_scope(SOMISANAScope.RESOURCE_ADMIN)
def test_add_file_resource(api, scopes):
    authorized = SOMISANAScope.RESOURCE_ADMIN in scopes

    product = ProductFactory.create(id=0)

    file_name = 'mock_resource_file.png'
    mock_file_path = f'{Path(__file__).parent}/test_data/{file_name}'

    title = "Product Thumbnail"
    resource_type = ResourceType.THUMBNAIL.value

    with open(mock_file_path, "rb") as f:
        file_to_upload = {'file': (file_name, f.read(), 'application/octet-stream')}

        r = api(scopes).put(
            f'/product/{product.id}/resource/?resource_type={resource_type}&title={title}',
            files=file_to_upload
        )

    if not authorized:
        assert_forbidden(r)
    else:

        stored_resource_path = f'{local_resource_folder_path}/product/{product.id}'

        assert filecmp.cmp(mock_file_path, f'{stored_resource_path}/{file_name}', shallow=False)

        shutil.rmtree(stored_resource_path)

