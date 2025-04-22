from typing import Optional, List

from pydantic import BaseModel

from .resource import ResourceModel


class SimulationModel(BaseModel):
    id: Optional[int]
    title: str
    folder_path: str
    data_access_url: Optional[str]
    cover_image: Optional[ResourceModel]

