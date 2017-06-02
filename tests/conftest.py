from membership.database import base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def pytest_configure(config):
    base.engine = create_engine('sqlite://', pool_size=10, pool_recycle=3600)
    base.Session = sessionmaker(bind=base.engine)