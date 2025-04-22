from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from somisana.db import Base


class Resource(Base):
    """
    A Resource is a link or a path to a document, image or other file type that relates to a product
    """

    __tablename__ = 'resource'

    id = Column(Integer, primary_key=True)
    reference = Column(String, nullable=False)
    reference_type = Column(String, nullable=True)
    resource_type = Column(String, nullable=False)

    resource_products = relationship('ProductResource', viewonly=True)
    products = association_proxy('resource_products', 'product')

    resource_simulations = relationship('SimulationResource', viewonly=True)
    simulations = association_proxy('resource_simulations', 'simulation')

