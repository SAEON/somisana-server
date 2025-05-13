from typing import Optional, List

from pydantic import BaseModel

from .resource import ResourceModel


class DatasetInModel(BaseModel):
    id: Optional[int]
    product_id: int
    title: str
    folder_path: str


class DatasetModel(BaseModel):
    id: Optional[int]
    product_id: int
    title: str
    folder_path: str
    data_access_urls: Optional[List[ResourceModel]]
    cover_image: Optional[ResourceModel]

