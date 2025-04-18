from typing import Optional

from pydantic import BaseModel

from .simulation import SimulationModel


class ProductModel(BaseModel):
    id: Optional[int]
    title: str
    description: str
    doi: Optional[str]
    north_bound: float
    south_bound: float
    east_bound: float
    west_bound: float
    simulations: Optional[list[SimulationModel]]


class ProductIn(BaseModel):
    title: str
    description: str
    doi: Optional[str]
    north_bound: float
    south_bound: float
    east_bound: float
    west_bound: float
    simulation_ids: Optional[list[int]]
