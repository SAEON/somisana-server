from pydantic import BaseModel


class ResourceModel(BaseModel):
    reference: str
    resource_type: str
    reference_type: str

