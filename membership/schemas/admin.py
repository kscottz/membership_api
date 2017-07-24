from graphene_sqlalchemy import SQLAlchemyObjectType

from membership.database.models import *
from .util import *

resolver = SchemaResolver()


# Full database models

class MemberSchema(SQLAlchemyObjectType):
    class Meta:
        model = Member

    name = g.String()
    resolve_name = resolver.field(name)  # TODO Allow extending from a Schema type that supports SQLAlchemy


class CommitteeSchema(SQLAlchemyObjectType):
    class Meta:
        model = Committee


class RoleSchema(SQLAlchemyObjectType):
    class Meta:
        model = Role


class MeetingSchema(SQLAlchemyObjectType):
    class Meta:
        model = Meeting


class AttendeeSchema(SQLAlchemyObjectType):
    class Meta:
        model = Attendee


class ElectionSchema(SQLAlchemyObjectType):
    class Meta:
        model = Election


class CandidateSchema(SQLAlchemyObjectType):
    class Meta:
        model = Candidate


class VoteSchema(SQLAlchemyObjectType):
    class Meta:
        model = Vote


class RankingSchema(SQLAlchemyObjectType):
    class Meta:
        model = Ranking


class EligibleVoterSchema(SQLAlchemyObjectType):
    class Meta:
        model = EligibleVoter
