from typing import Optional, List

from pydantic import BaseModel

from somisana.const import DatasetType
from .resource import ResourceModel


class DatasetInModel(BaseModel):
    id: Optional[int]
    product_id: Optional[int]
    identifier: str
    type: DatasetType
    title: str
    folder_path: str


class DatasetModel(BaseModel):
    id: Optional[int]
    product_id: int
    title: str
    folder_path: str
    identifier: str
    type: DatasetType
    data_access_urls: Optional[List[ResourceModel]]
    cover_image: Optional[ResourceModel]

