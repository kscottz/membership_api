from inspect import signature
from typing import Any, Callable, Dict, Union

import graphene as g
from graphene.types.objecttype import ObjectTypeMeta
from graphene.types.scalars import ScalarTypeMeta
from graphql.execution.base import ResolveInfo

from membership.util.functional import optionally


class ResolveEnv:
    def __init__(self, args: dict, context: dict, info: ResolveInfo):
        self.args = args
        self.context = context
        self.info = info


class SchemaMeta(ObjectTypeMeta):

    def __init__(cls, name, parents, dct):
        for field_name, field in cls._meta.fields.items():
            resolver_name = 'resolve_{}'.format(field_name)
            if getattr(cls, resolver_name, None) is None:
                field.resolver = Schema.resolver(field_name)
        super().__init__(name, parents, dct)


class Schema(g.ObjectType, metaclass=SchemaMeta):
    """
    Extending from Schema provides a helpful constructor that takes an ORM model and extracts
    the values from the ORM model that match this class's schema and do not require joins.

    By default, you do not need to define any resolvers except when the model name does not match
    the schema name, or the method for resolving the schema requires special logic.

    This class is also contains helpful static methods and decorators for building graphene schemas.
    """

    def __init__(self, model, **kwargs):
        self._model = model
        # Automatically extract all shallow field values from the ORM
        fields = self.extract_fields_shallow(model)
        fields.update(kwargs)
        super().__init__(**fields)

    @staticmethod
    def ref(classname: str) -> str:
        """
        Creates an absolute module path to the given graphene schema.

        Useful for avoiding cyclical references.

        :param classname: the relative name of the class
        :return: a full path to the given class
        """
        return 'membership.schemas.graphql.' + classname

    @staticmethod
    def resolver(f: Union[Callable, str]) -> Callable[['Schema', dict, dict, ResolveInfo], Any]:
        """
        Use as a decorator or pass the name of a schema field to create a self-bound function.

        As a decorator, you can use @staticmethod, accept self, or accept self and a ResolveEnv

        >>> class Example:
        ...     a = g.String()
        ...     b = g.String()
        ...     c = g.String()
        ...     @staticmethod
        ...     @Schema.resolver
        ...     def resolve_a():
        ...         return 'dummy value'
        ...     @Schema.resolver
        ...     def resolve_b(self):
        ...         return self._model.b
        ...     @Schema.resolver
        ...     def resolve_c(self, env: ResolveEnv):
        ...         return self.env.context.get('c')

        As a function builder, it will automatically handle any Field, NonNull, or List as long as the containing
        class extends from Schema and the referenced field type is a subclass of Schema.

        >>> class Example(Schema):
        ...     a = g.Field('Nested')
        ...     b = g.List('Nested')
        ...     c = g.NonNull('Nested')
        ...     resolve_a = Schema.resolver('a')
        ...     resolve_b = Schema.resolver('b')
        ...     resolve_c = Schema.resolver('c')
        ... class Nested(Schema):
        ...     name = g.String

        :param f: either the name of a field in this class's schema or a resolve function to decorate
        :return: a resolver function that, when named resolve_<field>, will be used to resolve a field in
                 this schema
        """
        # TODO: Allow mapping a field name to another name
        if isinstance(f, str):
            def wrapped_resolve(self: Schema, args: dict, context: dict, info: ResolveInfo) -> Any:
                field = self._meta.fields[f]
                field_type = field.type
                # If this field is a scalar, then we don't need to look at the field.type, just return the field value
                if isinstance(field_type, ScalarTypeMeta):
                    return getattr(self, f, getattr(self._model, f, None))
                elif isinstance(field_type, g.List):
                    # This is a field containing a list, map each element of the list to the expected schema type
                    cls = field_type.of_type
                    return [cls(x) for x in getattr(self._model, f)]
                elif isinstance(field_type, g.NonNull):
                    # This is a field containing a schema, map field value to the expected schema type
                    cls = field_type.of_type
                    value = getattr(self, f, getattr(self._model, f, None))
                    if value is None:
                        raise ValueError('Value of non-null field {}.{} cannot be None'.format(type(self), f))
                    return value if isinstance(cls, ScalarTypeMeta) else cls(value)
                # TODO: Handle List(NonNull), NonNull(List), List(Scalar) with recursion
                else:
                    cls = field_type
                    optional_value = getattr(self._model, f)
                    return optionally(cls, optional_value)
        elif callable(f):
            def wrapped_resolve(self, args: dict, context: dict, info: ResolveInfo) -> Any:
                sig = signature(f)
                num_args = len(sig.parameters)
                if num_args == 0:
                    return f()
                elif num_args == 1:
                    return f(self)
                else:
                    env = ResolveEnv(args, context, info)
                    return f(self, env)
            return wrapped_resolve
        else:
            raise ValueError('Expected decorated resolver function or str field name, not {}'.format(type(f)))
        return wrapped_resolve

    def extract_fields_shallow(self, instance) -> Dict[str, Any]:
        """
        Extracts the column values of a given ORM model that match the given class or Schema instance's
        fields and do not require traversing relationships.

        :param self: either the instance of this schema class or a Schema class object
        :param instance: an instance of an ORM model
        :return: a dict containing the keys of the fields in this schema that are named
                 the same as the scalar columns in the given ORM model and the field values
                 extracted from the given ORM model using getattr
        """
        col_names = [c.name for c in instance.__table__.columns]
        fields = self._meta.fields
        return {field: getattr(instance, field) for field in col_names if field in fields}
