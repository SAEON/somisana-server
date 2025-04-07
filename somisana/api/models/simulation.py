from typing import Optional

from pydantic import BaseModel


class SimulationModel(BaseModel):
    id: Optional[int]
    title: str
    folder_path: str
    data_access_url: Optional[str]

