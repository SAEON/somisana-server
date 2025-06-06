from typing import Optional

from pydantic import BaseModel

from .dataset import DatasetModel
from .resource import ResourceModel


class ProductModel(BaseModel):
    title: str
    description: str
    north_bound: float
    south_bound: float
    east_bound: float
    west_bound: float
    horizontal_resolution: Optional[str]
    vertical_extent: Optional[str]
    vertical_resolution: Optional[str]
    temporal_extent: Optional[str]
    temporal_resolution: Optional[str]
    variables: Optional[str]
    doi: Optional[str]
    superseded_product_id: Optional[int]


class ProductOut(ProductModel):
    id: Optional[int]
    datasets: Optional[list[DatasetModel]]
    resources: Optional[list[ResourceModel]]
    superseded_by_product_id: Optional[int]


class CatalogProductModel(BaseModel):
    id: Optional[int]
    title: str
    description: str
    doi: Optional[str]
    thumbnail: Optional[ResourceModel]
