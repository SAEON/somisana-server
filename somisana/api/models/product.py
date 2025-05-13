from typing import Optional

from pydantic import BaseModel

from .dataset import DatasetModel
from .resource import ResourceModel


class ProductModel(BaseModel):
    id: Optional[int]
    title: str
    description: str
    doi: Optional[str]
    north_bound: float
    south_bound: float
    east_bound: float
    west_bound: float
    datasets: Optional[list[DatasetModel]]
    resources: Optional[list[ResourceModel]]


class CatalogProductModel(BaseModel):
    id: Optional[int]
    title: str
    description: str
    doi: Optional[str]
    thumbnail: Optional[ResourceModel]


class ProductIn(BaseModel):
    title: str
    description: str
    doi: Optional[str]
    north_bound: float
    south_bound: float
    east_bound: float
    west_bound: float
    simulation_ids: Optional[list[int]]
