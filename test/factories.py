import random

import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from sqlalchemy.orm import scoped_session, sessionmaker

import somisana.db
from somisana.const import ResourceType, ResourceReferenceType
from somisana.db.models import Product, Simulation, Resource

FactorySession = scoped_session(sessionmaker(
    bind=somisana.db.engine,
    autocommit=False,
    autoflush=False,
    future=True,
))

fake = Faker()


class SOMISANAModelFactory(SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = FactorySession
        sqlalchemy_session_persistence = 'commit'


class ProductFactory(SOMISANAModelFactory):
    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n)
    title = factory.Faker('catch_phrase')
    description = factory.Faker('sentence')
    doi = factory.Faker('uuid4')
    south_bound = factory.Faker('pyfloat', left_digits=2, right_digits=6, min_value=-90, max_value=-10)
    north_bound = factory.LazyAttribute(lambda o: random.uniform(o.south_bound, 0))
    west_bound = factory.Faker('pyfloat', left_digits=3, right_digits=6, min_value=-180, max_value=170)
    east_bound = factory.LazyAttribute(lambda o: random.uniform(o.west_bound, 180))

    @factory.post_generation
    def simulations(obj, create, simulations):
        if simulations:
            for simulation in simulations:
                obj.simulations.append(simulation)
            if create:
                FactorySession.commit()


class SimulationFactory(SOMISANAModelFactory):
    class Meta:
        model = Simulation

    id = factory.Sequence(lambda n: n)
    title = factory.Faker('catch_phrase')
    folder_path = factory.Faker('file_path', depth=3)
    data_access_url = factory.Faker('uri')


class ResourceFactory(SOMISANAModelFactory):
    class Meta:
        model = Resource

    id = factory.Sequence(lambda n: n)
    product_id = factory.SelfAttribute('product.id')
    reference = factory.Faker('uri')
    reference_type = factory.LazyAttribute(lambda _: random.choice(list(ResourceReferenceType)).value)
    resource_type = factory.LazyAttribute(lambda _: random.choice(list(ResourceType)).value)

    product = factory.SubFactory(ProductFactory)
