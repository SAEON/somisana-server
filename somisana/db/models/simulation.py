from sqlalchemy import Column, Numeric, String, Integer, DateTime, ForeignKey
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
