import filecmp
import shutil
from pathlib import Path

import pytest

from somisana.api.lib import local_resource_folder_path
from somisana.const import SOMISANAScope, ResourceType, ResourceReferenceType
from test import TestSession
from somisana.db.models import Dataset, Resource
from test.api import assert_forbidden
from test.api.lib import compare_datasets, compare_resources
from test.factories import DatasetFactory, ProductFactory, ResourceFactory, DatasetResourceFactory


@pytest.mark.require_scope(SOMISANAScope.DATASET_READ)
def test_list_datasets(api, scopes):
    authorized = SOMISANAScope.DATASET_READ in scopes

    batch_size = 5
    DatasetFactory.create_batch(batch_size)

    r = api(scopes).get('/dataset/all/')

    if not authorized:
        assert_forbidden(r)
    else:
        assert len(r.json()) == batch_size


@pytest.mark.require_scope(SOMISANAScope.DATASET_READ)
def test_list_product_datasets(api, scopes):
    authorized = SOMISANAScope.DATASET_READ in scopes

    product = ProductFactory.create()

    batch_size = 5
    DatasetFactory.create_batch(batch_size, product=product)

    r = api(scopes).get(f'/dataset/product_datasets/{product.id}')

    if not authorized:
        assert_forbidden(r)
    else:
        assert len(r.json()) == batch_size


@pytest.mark.require_scope(SOMISANAScope.DATASET_READ)
def test_get_dataset(api, scopes):
    authorized = SOMISANAScope.DATASET_READ in scopes

    dataset = DatasetFactory.create()

    cover_image_resource = ResourceFactory.create(resource_type=ResourceType.COVER_IMAGE)
    data_access_url_resource = ResourceFactory.create(resource_type=ResourceType.DATA_ACCESS_URL)

    DatasetResourceFactory.create(dataset=dataset, resource=cover_image_resource)
    DatasetResourceFactory.create(dataset=dataset, resource=data_access_url_resource)

    r = api(scopes).get(f'/dataset/{dataset.id}')

    if not authorized:
        assert_forbidden(r)
    else:
        dataset_json = r.json()
        compare_datasets(dataset, dataset_json)
        compare_resources(cover_image_resource, dataset_json['cover_image'])
        compare_resources(data_access_url_resource, dataset_json['data_access_urls'][0])


@pytest.mark.require_scope(SOMISANAScope.DATASET_ADMIN)
def test_create_dataset(api, scopes):
    authorized = SOMISANAScope.DATASET_ADMIN in scopes

    product = ProductFactory.create()

    dataset = DatasetFactory.build(product=product)

    r = api(scopes).post('/dataset/', json=dict(
        product_id=dataset.product_id,
        title=dataset.title,
        folder_path=dataset.folder_path
    ))

    if not authorized:
        assert_forbidden(r)
    else:
        new_dataset_id = r.json()

        created_dataset = TestSession.get(Dataset, new_dataset_id)

        # Set the built dataset id to the created one, so they can be compared
        dataset.id = new_dataset_id

        compare_datasets(dataset, created_dataset.to_dict())


@pytest.mark.require_scope(SOMISANAScope.DATASET_ADMIN)
def test_update_dataset(api, scopes):
    authorized = SOMISANAScope.DATASET_ADMIN in scopes

    product = ProductFactory.create()

    dataset = DatasetFactory.create(product=product)

    updated_dataset = DatasetFactory.build(product=product)

    r = api(scopes).put(f'/dataset/{dataset.id}', json=dict(
        product_id=updated_dataset.product_id,
        title=updated_dataset.title,
        folder_path=updated_dataset.folder_path
    ))

    if not authorized:
        assert_forbidden(r)
    else:
        created_dataset = TestSession.get(Dataset, dataset.id)

        # Set the updated dataset id to the created dataset id to compare
        updated_dataset.id = created_dataset.id

        compare_datasets(updated_dataset, created_dataset.to_dict())


@pytest.mark.require_scope(SOMISANAScope.DATASET_ADMIN)
def test_delete_dataset(api, scopes):
    authorized = SOMISANAScope.DATASET_ADMIN in scopes

    dataset = DatasetFactory.create()

    r = api(scopes).delete(f'/dataset/{dataset.id}')

    if not authorized:
        assert_forbidden(r)
    else:
        assert TestSession.get(Dataset, dataset.id) is None


@pytest.mark.require_scope(SOMISANAScope.DATASET_ADMIN)
def test_add_resource(api, scopes):
    authorized = SOMISANAScope.DATASET_ADMIN in scopes

    dataset = DatasetFactory.create()

    resource = ResourceFactory.build(
        resource_type=ResourceType.COVER_IMAGE,
        reference_type=ResourceReferenceType.LINK
    )

    r = api(scopes).delete(f'/dataset/{dataset.id}/resource', json=dict(
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

    dataset = DatasetFactory.create(id=0)

    file_name = 'mock_resource_file.png'
    mock_file_path = f'{Path(__file__).parent}/test_data/{file_name}'

    title = "Dataset Cover Image"
    resource_type = ResourceType.COVER_IMAGE.value

    with open(mock_file_path, "rb") as f:
        file_to_upload = {'file': (file_name, f.read(), 'application/octet-stream')}

        r = api(scopes).put(
            f'/dataset/{dataset.id}/resource/?resource_type={resource_type}&title={title}',
            files=file_to_upload
        )

    if not authorized:
        assert_forbidden(r)
    else:

        stored_resource_path = f'{local_resource_folder_path}/dataset/{dataset.id}'

        assert filecmp.cmp(mock_file_path, f'{stored_resource_path}/{file_name}', shallow=False)

        shutil.rmtree(stored_resource_path)