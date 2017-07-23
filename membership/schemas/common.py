import graphene as g
from graphene.types.scalars import StringValue, IntValue

from .util import Schema


class ID(g.Scalar):
    """
    Parses input string or number as an integer.

    This allows the UI to pass strings and not worry about the id encoded in the database.
    """

    serialize = str
    parse_value = int

    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, (StringValue, IntValue)):
            return int(ast.value)


class EntitySchema(Schema):
    """
    The root of every identifiable entity in the system.

    Provides the id field.
    """
    id = g.NonNull(ID)
