from typing import Optional

from pydantic import BaseModel


class SimulationModel(BaseModel):
    id: int
    folder_path: str
    data_access_url: Optional[str]


class SimulationIn(BaseModel):
    title: str
    folder_path: str
    data_access_url: Optional[str]
