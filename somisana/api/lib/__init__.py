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
    file_path = save_local_resource_file(entity_type.value, entity_id, file)

    resource = Resource(
        title=resource_model.title,
        resource_type=resource_model.resource_type,
        reference=file_path,
        reference_type=ResourceReferenceType.PATH
    )

    resource.save()

    return resource.id


def save_local_resource_file(entity_type: EntityType, entity_id: int, local_file: UploadFile) -> str:
    local_resource_leaf_dir = f'{entity_type}/{entity_id}'
    local_resource_full_dir = f"{Path.home()}/somisana/resources/{local_resource_leaf_dir}"

    if not os.path.exists(local_resource_full_dir):
        os.makedirs(local_resource_full_dir)

    file_path = f"{local_resource_full_dir}/{local_file.filename}"

    with open(file_path, "wb") as f:
        f.write(local_file.file.read())

    return f'{local_resource_leaf_dir}/{local_file.filename}'


def delete_local_resource_file(resource_path):
    resource_full_path = f'{Path.home()}/somisana/resources/{resource_path}'
    if os.path.exists(resource_full_path):
        os.remove(resource_full_path)
