from typing import Optional

from pydantic import BaseModel
from somisana.const import ResourceType, ResourceReferenceType


class ResourceModel(BaseModel):
    id: Optional[str]
    product_id: int
    reference: str
    resource_type: ResourceType
    reference_type: Optional[ResourceReferenceType]

