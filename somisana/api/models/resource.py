from typing import Optional

from pydantic import BaseModel

from somisana.const import ResourceType, ResourceReferenceType


class ResourceModel(BaseModel):
    id: Optional[str]
    title: Optional[str]
    reference: Optional[str]
    resource_type: ResourceType
    reference_type: Optional[ResourceReferenceType]


class ProductResourceModel(ResourceModel):
    product_id: int


class SimulationResourceModel(ResourceModel):
    simulation_id: int
