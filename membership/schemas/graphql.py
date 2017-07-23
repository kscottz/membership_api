from inspect import signature
from typing import Callable, Dict

import graphene as g
from graphene.types.datetime import DateTime
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql.execution.base import ResolveInfo
from graphql.language.ast import IntValue, StringValue
from sqlalchemy.orm.query import Query

from membership.database import models
from membership.database.models import *
from membership.util.functional import optionally


# Full database models

class MemberSchema(SQLAlchemyObjectType):
    class Meta:
        model = models.Member

    name = g.String()

    def resolve_name(self, args: dict, context: dict, info: ResolveInfo):
        return self.name


class CommitteeSchema(SQLAlchemyObjectType):
    class Meta:
        model = models.Committee


class RoleSchema(SQLAlchemyObjectType):
    class Meta:
        model = models.Role


class MeetingSchema(SQLAlchemyObjectType):
    class Meta:
        model = models.Meeting


class AttendeeSchema(SQLAlchemyObjectType):
    class Meta:
        model = models.Attendee


class ElectionSchema(SQLAlchemyObjectType):
    class Meta:
        model = models.Election


class CandidateSchema(SQLAlchemyObjectType):
    class Meta:
        model = models.Candidate


class VoteSchema(SQLAlchemyObjectType):
    class Meta:
        model = models.Vote


class RankingSchema(SQLAlchemyObjectType):
    class Meta:
        model = models.Ranking


class EligibleVoterSchema(SQLAlchemyObjectType):
    class Meta:
        model = models.EligibleVoter


# API View Models

# def ref(classname: str) -> str:
#     return 'membership.schemas.graphql.' + classname


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


class ResolveEnv:
    def __init__(self, args: dict, context: dict, info: ResolveInfo):
        self.args = args
        self.context = context
        self.info = info


class Schema(g.ObjectType):
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
        # TODO: Automatically setup all the resolver functions for the schema using a metaclass
        # for field_name, field_schema in self._meta.fields.items():
        #     if field_name not in fields and getattr(self, field_name, None) is None:
        #         setattr(self.__class__, 'resolve_{}'.format(field_name), Schema.resolver(field_name))
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
                if isinstance(field, g.Scalar):
                    return getattr(self._model, f)
                elif isinstance(field_type, g.List):
                    # This is a field containing a list, map each element of the list to the expected schema type
                    cls = field_type.of_type
                    return [cls(x) for x in getattr(self._model, f)]
                elif isinstance(field_type, g.NonNull):
                    # This is a field containing a schema, map field value to the expected schema type
                    cls = field_type.of_type
                    value = getattr(self._model, f)
                    if value is None:
                        raise ValueError('Value of non-null field {}.{} cannot be None'.format(type(self), f))
                    return cls(value)
                # TODO: Handle List(NonNull), NonNull(List), List(Scalar)
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

    def extract_fields_shallow(self_or_cls, instance: Base) -> Dict[str, Any]:
        """
        Extracts the column values of a given ORM model that match the given class or Schema instance's
        fields and do not require traversing relationships.

        :param self_or_cls: either the instance of this schema class or a Schema class object
        :param instance: an instance of an ORM model
        :return: a dict containing the keys of the fields in this schema that are named
                 the same as the scalar columns in the given ORM model and the field values
                 extracted from the given ORM model using getattr
        """
        col_names = [c.name for c in instance.__table__.columns]
        fields = self_or_cls._meta.fields
        return {field: getattr(instance, field) for field in col_names if field in fields}


class EntityFields(g.AbstractType):
    """
    The root of every identifiable entity in the system.

    Provides the id field.
    """
    id = g.NonNull(ID)


class EntitySchema(EntityFields, Schema):
    pass


class PubElectionSchema(EntitySchema):
    name = g.NonNull(g.String)
    status = g.NonNull(g.String)
    number_winners = g.NonNull(g.Int)

    candidates = g.List(Schema.ref('PubCandidateSchema'))
    votes = g.List(Schema.ref('PubVoteSchema'))


class PubCandidateSchema(EntitySchema):
    member_id = g.Int()
    election_id = g.Int()
    name = g.String()
    biography = g.String()

    election = g.Field(Schema.ref('PubElectionSchema'))

    def __init__(self, model: Candidate):
        super().__init__(model)
        self.name = model.member.name
        self.biography = model.member.biography


class PubVoteSchema(EntitySchema):
    vote_key = g.Int()
    election_id = ID()

    election = g.Field(Schema.ref('PubElectionSchema'))
    ranking = g.List(Schema.ref('PubRankingSchema'))
    ranked_candidates = g.List(Schema.ref('PubCandidateSchema'))


class PubRankingSchema(EntitySchema):
    vote_id = ID()
    rank = g.Int()
    candidate_id = ID()

    vote = g.Field(Schema.ref('PubVoteSchema'))
    candidate = g.Field(Schema.ref('PubCandidateSchema'))


class PubCommitteeSchema(EntitySchema):
    name = g.String()


class PubMeetingSchema(EntitySchema):
    short_id = ID()
    name = g.String()
    committee_id = ID()
    start_time = DateTime()
    end_time = DateTime()

    attendees = g.List(Schema.ref('PubAttendeeSchema'))


class PubAttendeeSchema(EntitySchema):
    meeting_id = ID()
    member_id = ID()

    meeting = g.Field(Schema.ref('PubMeetingSchema'))


class MyEligibleVoterSchema(EntitySchema):
    voted = g.Boolean()
    election_id = ID()

    election = g.Field(Schema.ref('PubElectionSchema'))


class MyRole(EntitySchema):
    committee_id = ID()
    name = g.NonNull(g.String)

    committee = g.Field(Schema.ref('PubCommitteeSchema'))

    def __init__(self, model: Role):
        super().__init__(model)
        self.name = model.role


class MyUserSchema(EntitySchema):
    first_name = g.String()
    last_name = g.String()
    name = g.String()
    email_address = g.String()
    biography = g.String()

    committees = g.List(Schema.ref('PubCommitteeSchema'))
    eligible_votes = g.List(Schema.ref('MyEligibleVoterSchema'))
    meetings_attended = g.List(Schema.ref('PubMeetingSchema'))
    roles = g.List(Schema.ref('MyRole'))


class QuerySchema(g.ObjectType):
    all_attendees = g.List(AttendeeSchema)
    all_candidates = g.List(CandidateSchema)
    all_committees = g.List(CommitteeSchema)
    all_elections = g.List(ElectionSchema)
    all_eligible_voters = g.List(EligibleVoterSchema)
    all_meetings = g.List(MeetingSchema)
    all_members = g.List(MemberSchema, id=g.Argument(ID))
    all_rankings = g.List(RankingSchema)
    all_roles = g.List(RoleSchema)
    all_votes = g.List(VoteSchema)

    public_elections = g.List(PubElectionSchema)

    my_user = g.Field(MyUserSchema)

    def resolve_all_attendees(self, args: dict, context: dict, info: ResolveInfo):
        query: Query = AttendeeSchema.get_query(context)
        return query.all()

    def resolve_all_candidates(self, args: dict, context: dict, info: ResolveInfo):
        query: Query = CandidateSchema.get_query(context)
        return query.all()

    def resolve_all_committees(self, args: dict, context: dict, info: ResolveInfo):
        query: Query = CommitteeSchema.get_query(context)
        return query.all()

    def resolve_all_elections(self, args: dict, context: dict, info: ResolveInfo):
        query: Query = ElectionSchema.get_query(context)
        return query.all()

    def resolve_all_eligible_voters(self, args: dict, context: dict, info: ResolveInfo):
        query: Query = EligibleVoterSchema.get_query(context)
        return query.all()

    def resolve_all_meetings(self, args: dict, context: dict, info: ResolveInfo):
        query: Query = MeetingSchema.get_query(context)
        return query.all()

    def resolve_all_members(self, args: dict, context: dict, info: ResolveInfo):
        requester: Member = context['requester']
        query: Query = MemberSchema.get_query(context)
        filter_id = args.get('id')
        if requester.is_admin():
            query = query.filter(Member.id == filter_id)
            return query.all()
        else:
            return [requester] if not filter_id else \
                requester if requester.id == filter_id else []

    def resolve_public_elections(self, args: dict, context: dict, info: ResolveInfo):
        query: Query = ElectionSchema.get_query(context)
        all: List[Election] = query.all()
        return all

    def resolve_all_rankings(self, args: dict, context: dict, info: ResolveInfo):
        query: Query = RankingSchema.get_query(context)
        return query.all()

    def resolve_all_roles(self, args: dict, context: dict, info: ResolveInfo):
        query: Query = RoleSchema.get_query(context)
        return query.all()

    def resolve_all_votes(self, args: dict, context: dict, info: ResolveInfo):
        query: Query = VoteSchema.get_query(context)
        return query.all()

    def resolve_my_user(self, args: dict, context: dict, info: ResolveInfo):
        requester: Member = context['requester']
        x = MyUserSchema(requester)
        return x


schema = g.Schema(query=QuerySchema)
