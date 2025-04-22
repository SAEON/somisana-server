import os
from pathlib import Path

from fastapi import UploadFile

from somisana.api.lib.auth import Authorize
from somisana.api.lib.auth import Authorize
from somisana.api.models import ResourceModel
from somisana.const import EntityType
from somisana.const import ResourceReferenceType
from somisana.db.models import Resource


def save_file_resource(file: UploadFile, resource_model: ResourceModel, entity_type: EntityType, entity_id: int) -> int:
    file_path = save_local_resource_file(entity_type, entity_id, file)

    resource = Resource(
        resource_type=resource_model.resource_type,
        reference=file_path,
        reference_type=ResourceReferenceType.PATH
    )

    resource.save()

    return resource.id


def save_local_resource_file(entity_type: EntityType, entity_id: int, local_file: UploadFile) -> str:
    product_local_resource_dir = f"{Path.home()}/somisana/resources/{entity_type}/{entity_id}"

    if not os.path.exists(product_local_resource_dir):
        os.makedirs(product_local_resource_dir)

    file_path = f"{product_local_resource_dir}/{local_file.filename}"

    with open(file_path, "wb") as f:
        f.write(local_file.file.read())

    return file_path


def delete_local_resource_file(resource_path):
    if os.path.exists(resource_path):
        os.remove(resource_path)
