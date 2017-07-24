import inspect
from inspect import signature
from typing import Any, Callable, Dict, Optional, Union

import graphene as g
from graphene.types.unmountedtype import OrderedType
from graphene.types.objecttype import ObjectTypeMeta
from graphene.types.scalars import ScalarTypeMeta
from graphql.execution.base import ResolveInfo

from membership.util.functional import optionally

# A type alias for the resolver function expected by graphene
ResolverCallable = Callable[['Schema', dict, dict, ResolveInfo], Any]


class ResolveEnv:
    def __init__(self, args: dict, context: dict, info: ResolveInfo):
        self.args = args
        self.context = context
        self.info = info


class SchemaResolver(Callable[[Union[Callable, str]], ResolverCallable]):

    def __init__(self, package: Optional[str] = None):
        if package is None:
            caller_stack = inspect.stack()[1]
            package = caller_stack.frame.f_locals['__name__']
        self.package = package

    def type(self, classname: str) -> str:
        """
        Creates an absolute module path to the given graphene schema.

        Useful for avoiding cyclical references.

        :param classname: the relative name of the class from this resolver
        :return: a full path to the given class
        """
        return '{}.{}'.format(self.package, classname)

    # TODO: Allow mapping a field name to another name
    # TODO: Allow passing a function instead of a string
    def field(self, field: Union[OrderedType, str], from_model: Optional[str] = None):
        """
        Create a resolver for a given field or field name.
        
        >>> resolver = SchemaResolver()
        >>> class Example(Schema):
        ...     a = g.Field('Nested')
        ...     b = g.List('Nested')
        ...     c = g.NonNull('Nested')
        ...     resolve_a = resolver.field(a)
        ...     resolve_b = resolver.field(b)
        ...     resolve_c = resolver.field(c)
        >>> class Nested(Schema):
        ...     name = g.String

        :param field: the unmounted field from the schema
        :param from_model: the unmounted field from the schema
        :return: a resolver function that, when named resolve_<field>, will be used to resolve a field in
                 this schema
        """
        if isinstance(field, str):
            field_name = field
            _field = None
        else:
            # Automatically extract the field name from the call stack
            # TODO: Test that this works for fields inherited from abstract types
            caller_frame_locals = inspect.stack()[1].frame.f_locals
            field_name = next(k for k, v in caller_frame_locals.items() if v is field)
            # Cache the field if given
            _field = field
        # Cache the field type of mounted fields and scalars
        _field_type = field.type if isinstance(field, g.Field) else \
            field if isinstance(field, g.Scalar) else None

        # TODO: Allow mapping a field name to another name
        def wrapped_resolve(schema: Schema, args: dict, context: dict, info: ResolveInfo) -> Any:
            field = _field or schema._meta.fields[field_name]
            field_type = _field_type or field.type
            # If this field is a scalar, then we don't need to look at the field.type, just return the field value
            if isinstance(field_type, ScalarTypeMeta):
                return getattr(schema, field_name, getattr(schema._model, field_name, None))
            elif isinstance(field_type, g.List):
                # This is a field containing a list, map each element of the list to the expected schema type
                cls = field_type.of_type
                return [cls(x) for x in getattr(schema._model, field_name)]
            elif isinstance(field_type, g.NonNull):
                # This is a field containing a schema, map field value to the expected schema type
                cls = field_type.of_type
                # TODO: Make this getattr logic reusable
                value = getattr(schema, field_name, getattr(schema._model, field_name, None))
                if value is None:
                    raise ValueError('Value of non-null field {}.{} cannot be None'.format(type(self), field_name))
                return value if isinstance(cls, ScalarTypeMeta) else cls(value)
            # TODO: Handle List(NonNull), NonNull(List), List(Scalar) with recursion
            else:
                cls = field_type
                optional_value = getattr(schema._model, field_name)
                return optionally(cls, optional_value)
        return wrapped_resolve

    def __call__(self, f: Callable) -> ResolverCallable:
        """
        Use as a decorator to convert the following function into a resolver with a friendlier API.

        You can use @staticmethod (to return a constant), self only (to access self._model), or
        you can accept both self and ResolveEnv, to have access to the args, context, and resolve info.

        >>> resolver = SchemaResolver()
        >>> class Example:
        ...     a = g.String()
        ...     b = g.String()
        ...     c = g.String()
        ...     @staticmethod
        ...     @resolver
        ...     def resolve_a():
        ...         return 'dummy value'
        ...     @resolver
        ...     def resolve_b(self):
        ...         return self._model.b
        ...     @resolver
        ...     def resolve_c(self, env: ResolveEnv):
        ...         return env.context.get('c')
        """
        def wrapped_resolve(schema: Schema, args: dict, context: dict, info: ResolveInfo) -> Any:
            sig = signature(f)
            num_args = len(sig.parameters)
            if num_args == 0:
                return f()
            elif num_args == 1:
                return f(schema)
            else:
                env = ResolveEnv(args, context, info)
                return f(schema, env)

        return wrapped_resolve


class SchemaMeta(ObjectTypeMeta):

    def __init__(cls, name, parents, dct):
        resolver = SchemaResolver(cls.__module__)
        for field_name, field in cls._meta.fields.items():
            resolver_name = 'resolve_{}'.format(field_name)
            # Only add an automatic resolver for a field if an explicit one does not exist
            if getattr(cls, resolver_name, None) is None:
                field.resolver = resolver.field(field_name)
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

    # TODO: Indicate that this is specific to SQL Alchemy and abstract it out
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
