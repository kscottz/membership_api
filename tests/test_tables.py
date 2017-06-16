from membership.database import models
from membership.database.base import engine, metadata, Base


class TestTables:

    def test_tables(self):
        metadata.create_all(engine)
        metadata.drop_all(engine)

    def test_constructors(self):
        """
        Mappers are constructed on first instantiation so test that models can be instantiated
        without throwing exceptions
        :return:
        """
        subclasses = Base.__subclasses__()
        for subclass in subclasses:
            subclass()
