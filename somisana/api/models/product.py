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
    horizontal_extent: Optional[float]
    horizontal_resolution: Optional[float]
    vertical_extent: Optional[float]
    vertical_resolution: Optional[float]
    temporal_extent: Optional[float]
    temporal_resolution: Optional[float]
    variables: Optional[str]
    datasets: Optional[list[DatasetModel]]
    resources: Optional[list[ResourceModel]]
    superseded_product_id: Optional[int]
    superseded_by_product_id: Optional[int]


class CatalogProductModel(BaseModel):
    id: Optional[int]
    title: str
    description: str
    doi: Optional[str]
    thumbnail: Optional[ResourceModel]


class ProductIn(BaseModel):
    title: str
    description: str
    north_bound: float
    south_bound: float
    east_bound: float
    west_bound: float
    horizontal_extent: Optional[float]
    horizontal_resolution: Optional[float]
    vertical_extent: Optional[float]
    vertical_resolution: Optional[float]
    temporal_extent: Optional[float]
    temporal_resolution: Optional[float]
    variables: Optional[str]
    doi: Optional[str]
    superseded_product_id: Optional[int]
