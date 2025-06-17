from somisana.const import SOMISANAScope
from test.factories import ProductFactory, DatasetFactory, ResourceFactory, ProductVersionFactory, \
    ProductResourceFactory, DatasetResourceFactory
from somisana.db.models import Product, Dataset, Resource
from test import TestSession
from test.api import assert_forbidden
import pytest


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

    dataset = DatasetFactory(product=product).create()
    dataset_resource = ResourceFactory(dataset=dataset).create()

    product_resource = ResourceFactory(product=product).create()

    r = api(scopes).get(f'/product/{product.id}/')

    if not authorized:
        assert_forbidden(r)
    else:
        fetched_product = r.json()


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

        # Set the build factories' id to the fetched products' id to compare them
        product.id = fetched_product.id

        assert (fetched_product.to_dict() == product.to_dict())
