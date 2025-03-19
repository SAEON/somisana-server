from sqlalchemy import Column, Numeric, String, Integer, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from somisana.db import Base


class Product(Base):
    """
    A Product contains metadata information that applies to one or more simulations.
    """

    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    doi = Column(String)
    north_bound = Column(Numeric, nullable=False)
    south_bound = Column(Numeric, nullable=False)
    east_bound = Column(Numeric, nullable=False)
    west_bound = Column(Numeric, nullable=False)

    product_simulations = relationship('ProductSimulation', cascade='all, delete-orphan', passive_deletes=True)
    simulations = association_proxy('product_simulations', 'simulation',
                                    creator=lambda s: ProductSimulation(simulation=s))
    resources = relationship('Resource', cascade='all, delete-orphan', passive_deletes=True, back_populates='product')


class ProductSimulation(Base):
    """
    Model of many-to-many product-simulation relationship.
    """

    __tablename__ = 'product_simulation'

    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), primary_key=True)
    simulation_id = Column(Integer, ForeignKey('simulation.id', ondelete='CASCADE'), primary_key=True)

    product = relationship('Product', viewonly=True)
    simulation = relationship('Simulation')
