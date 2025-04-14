from typing import Optional

from fastapi import UploadFile
from pydantic import BaseModel

from somisana.const import ResourceType, ResourceReferenceType


class ResourceModel(BaseModel):
    id: Optional[str]
    product_id: int
    reference: Optional[str]
    resource_type: ResourceType
    reference_type: Optional[ResourceReferenceType]

