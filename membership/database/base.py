from config.database_config import settings
from datetime import datetime
import json
from sqlalchemy import create_engine, event
from sqlalchemy.exc import DisconnectionError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.types as types


def checkout_listener(dbapi_con, con_record, con_proxy):
    """
    Ensures that connections in the pool are still valid before returning them
    :param dbapi_con:
    :param con_record:
    :param con_proxy:
    :return:
    """
    try:
        try:
            dbapi_con.ping(False)
        except TypeError:
            dbapi_con.ping()
    except dbapi_con.OperationalError as exc:
        if exc.args[0] in (2006, 2013, 2014, 2045, 2055):
            raise DisconnectionError()
        else:
            raise


Base = declarative_base()
metadata = Base.metadata
engine = create_engine(**settings)
Session = sessionmaker(bind=engine)
event.listen(engine, 'checkout', checkout_listener)


def date_parser(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d')


class StringyJSON(types.TypeDecorator):
    """Stores and retrieves JSON as TEXT."""

    impl = types.TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value

# TypeEngine.with_variant says "use StringyJSON instead when
# connecting to 'sqlite'"
JSON = types.JSON().with_variant(StringyJSON, 'sqlite')