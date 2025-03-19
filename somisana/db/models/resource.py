from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from somisana.db import Base


class Resource(Base):
    """
    A Resource is a link or a path to a document, image or other file type that relates to a product
    """

    __tablename__ = 'resource'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    reference = Column(String, nullable=False)
    reference_type = Column(String, nullable=True)
    resource_type = Column(String, nullable=False)

    product = relationship('Product', back_populates='resources')
