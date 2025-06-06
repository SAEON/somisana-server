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
    north_bound = Column(Numeric, nullable=False)
    south_bound = Column(Numeric, nullable=False)
    east_bound = Column(Numeric, nullable=False)
    west_bound = Column(Numeric, nullable=False)
    horizontal_resolution = Column(String, nullable=False)
    vertical_extent = Column(String, nullable=False)
    vertical_resolution = Column(String, nullable=False)
    temporal_extent = Column(String, nullable=False)
    temporal_resolution = Column(String, nullable=False)
    variables = Column(String, nullable=False)
    doi = Column(String)

    datasets = relationship("Dataset", back_populates="product")

    product_resources = relationship('ProductResource', cascade='all, delete-orphan', passive_deletes=True)
    resources = association_proxy('product_resources', 'resource',
                                  creator=lambda s: ProductResource(resource=s))

    supersedes = relationship('ProductVersion', foreign_keys='ProductVersion.product_id', back_populates='product',
                              uselist=False)
    superseded_by = relationship('ProductVersion', foreign_keys='ProductVersion.superseded_product_id',
                                 back_populates='superseded_product', uselist=False)


class ProductResource(Base):
    """
    Model of many-to-many product-resource relationship.
    """

    __tablename__ = 'product_resource'

    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), primary_key=True)
    resource_id = Column(Integer, ForeignKey('resource.id', ondelete='CASCADE'), primary_key=True)

    product = relationship('Product', viewonly=True)
    resource = relationship('Resource')


class ProductVersion(Base):
    """
    Relationship between a product it the product it superseeds
    """

    __tablename__ = 'product_version'

    product_id = Column(Integer, ForeignKey('product.id'), primary_key=True)
    superseded_product_id = Column(Integer, ForeignKey('product.id'), nullable=False)

    product = relationship('Product', foreign_keys=[product_id], back_populates='supersedes')
    superseded_product = relationship('Product', foreign_keys=[superseded_product_id], back_populates='superseded_by')
