from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from somisana.db import Base


class Dataset(Base):
    """
    A Dataset represents a folder that contains outputs
    """

    __tablename__ = 'dataset'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    title = Column(String, nullable=False)
    identifier = Column(String, nullable=False)
    type = Column(String, nullable=False)
    folder_path = Column(String, nullable=False)

    product = relationship('Product', back_populates='datasets')

    dataset_resources = relationship('DatasetResource', cascade='all, delete-orphan', passive_deletes=True)
    resources = association_proxy('dataset_resources', 'resource',
                                    creator=lambda s: DatasetResource(resource=s))


class DatasetResource(Base):
    """
    Model of many-to-many dataset-resource relationship.
    """

    __tablename__ = 'dataset_resource'

    dataset_id = Column(Integer, ForeignKey('dataset.id', ondelete='CASCADE'), primary_key=True)
    resource_id = Column(Integer, ForeignKey('resource.id', ondelete='CASCADE'), primary_key=True)

    dataset = relationship('Dataset', viewonly=True)
    resource = relationship('Resource')
