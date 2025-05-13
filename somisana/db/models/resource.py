from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from somisana.db import Base


class Resource(Base):
    """
    A Resource is a link or a path to a document, image or other file type that relates to a product or dataset
    """

    __tablename__ = 'resource'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    reference = Column(String, nullable=False)
    reference_type = Column(String, nullable=True)
    resource_type = Column(String, nullable=False)

    resource_products = relationship('ProductResource', viewonly=True)
    products = association_proxy('resource_products', 'product')

    resource_datasets = relationship('DatasetResource', viewonly=True)
    datasets = association_proxy('resource_datasets', 'dataset')
