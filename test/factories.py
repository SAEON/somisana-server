import random

import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from sqlalchemy.orm import scoped_session, sessionmaker

import somisana.db
from somisana.const import ResourceType, ResourceReferenceType
from somisana.db.models import Product, ProductVersion, ProductResource, Dataset, DatasetResource, Resource

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
    south_bound = factory.Faker('pydecimal', left_digits=3, right_digits=2, min_value=-180, max_value=170)
    north_bound = factory.Faker('pydecimal', left_digits=3, right_digits=2, min_value=-180, max_value=170)
    west_bound = factory.Faker('pydecimal', left_digits=3, right_digits=2, min_value=-180, max_value=170)
    east_bound = factory.Faker('pydecimal', left_digits=3, right_digits=2, min_value=-180, max_value=170)
    horizontal_resolution = factory.Faker('word')
    vertical_extent = factory.Faker('word')
    vertical_resolution = factory.Faker('word')
    temporal_extent = factory.Faker('word')
    temporal_resolution = factory.Faker('word')
    variables = factory.Faker('word')


class ProductVersionFactory(SOMISANAModelFactory):
    class Meta:
        model = ProductVersion

    product = factory.SubFactory(ProductFactory)
    superseded_product = factory.SubFactory(ProductFactory)


class DatasetFactory(SOMISANAModelFactory):
    class Meta:
        model = Dataset

    id = factory.Sequence(lambda n: n)
    product = factory.SubFactory(ProductFactory)
    title = factory.Faker('sentence', nb_words=3)
    folder_path = factory.Faker('file_path', depth=2, extension='nc')


class ResourceFactory(SOMISANAModelFactory):
    class Meta:
        model = Resource

    id = factory.Sequence(lambda n: n)
    title = factory.Faker('sentence', nb_words=3)
    reference = factory.Faker('uri')
    reference_type = factory.LazyAttribute(lambda _: random.choice(list(ResourceReferenceType)).value)
    resource_type = factory.LazyAttribute(lambda _: random.choice(list(ResourceType)).value)


class ProductResourceFactory(SOMISANAModelFactory):
    class Meta:
        model = ProductResource

    product_id = factory.SelfAttribute('product.id')
    resource_id = factory.SelfAttribute('resource.id')

    product = factory.SubFactory(ProductFactory)
    resource = factory.SubFactory(ResourceFactory)


class DatasetResourceFactory(SOMISANAModelFactory):
    class Meta:
        model = DatasetResource

    dataset_id = factory.SelfAttribute('dataset.id')
    resource_id = factory.SelfAttribute('resource.id')

    dataset = factory.SubFactory(DatasetFactory)
    resource = factory.SubFactory(ResourceFactory)


