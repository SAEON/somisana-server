from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from somisana.db import Base


class Simulation(Base):
    """
    A Simulation represents a folder that contains outputs
    """

    __tablename__ = 'simulation'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    folder_path = Column(String, nullable=False)
    data_access_url = Column(String, nullable=False)

    simulation_products = relationship('ProductSimulation', viewonly=True)
    products = association_proxy('simulation_products', 'product')

    simulation_resources = relationship('SimulationResource', cascade='all, delete-orphan', passive_deletes=True)
    resources = association_proxy('simulation_resources', 'resource',
                                    creator=lambda s: SimulationResource(resource=s))


class SimulationResource(Base):
    """
    Model of many-to-many simulation-resource relationship.
    """

    __tablename__ = 'simulation_resource'

    simulation_id = Column(Integer, ForeignKey('simulation.id', ondelete='CASCADE'), primary_key=True)
    resource_id = Column(Integer, ForeignKey('resource.id', ondelete='CASCADE'), primary_key=True)

    simulation = relationship('Simulation', viewonly=True)
    resource = relationship('Resource')
