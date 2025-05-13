import logging
import os
import pathlib
from dotenv import load_dotenv
from somisana.db import Base, engine
from somisana.db.models import Product, Dataset, Resource, ProductResource, DatasetResource

logger = logging.getLogger(__name__)


def initialize():
    logger.info('Initializing static system data...')

    load_dotenv(pathlib.Path(os.getcwd()) / '.env')  # for a local run; in a container there's no .env

    init_database_schema()

    logger.info('Done.')


def init_database_schema():
    Base.metadata.create_all(engine)
