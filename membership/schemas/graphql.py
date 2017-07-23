from typing import Dict

import graphene as g
from graphene.types.datetime import DateTime
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql.execution.base import ResolveInfo
from graphql.language.ast import IntValue, StringValue
from sqlalchemy.orm.query import Query

from membership.database import models
from membership.database.models import *


# def extract_fields(model: models.Base):
#     cols = model.__table__.columns
#     return {k: getattr(model, k) for k in vars(model) if not k.startswith('_')}


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

def _reltype(classname: str) -> str:
    return 'membership.schemas.graphql.' + classname


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


class EntityFields(g.AbstractType):
    """
    The root of every identifiable entity in the system.

    Provides the id field.
    """
    id = g.NonNull(ID)


class PubElectionSchema(g.ObjectType, EntityFields):
    name = g.NonNull(g.String)
    status = g.NonNull(g.String)
    number_winners = g.NonNull(g.Int)

    candidates = g.List(_reltype('PubCandidateSchema'))
    votes = g.List(_reltype('PubVoteSchema'))


class PubCandidateSchema(g.ObjectType, EntityFields):
    member_id = g.Int()
    election_id = g.Int()
    name = g.String()
    biography = g.String()

    election = g.Field(_reltype('PubElectionSchema'))


class PubVoteSchema(g.ObjectType, EntityFields):
    vote_key = g.Int()
    election_id = ID()

    election = g.Field(_reltype('PubElectionSchema'))
    ranking = g.List(_reltype('PubRankingSchema'))

    ranked_candidates = g.List(_reltype('PubCandidateSchema'))


class PubRankingSchema(g.ObjectType, EntityFields):
    vote_id = ID()
    rank = g.Int()
    candidate_id = ID()

    vote = g.Field(_reltype('PubVoteSchema'))
    candidate = g.Field(_reltype('PubCandidateSchema'))


class PubCommitteeSchema(g.ObjectType, EntityFields):
    name = g.String()

    def __init__(self, model: models.Committee):
        # fields = extract_fields(model)
        all_kwargs = {
            'name': model.name
        }
        super().__init__(**all_kwargs)


class PubMeetingSchema(g.ObjectType, EntityFields):
    short_id = ID()
    name = g.String()
    committee_id = ID()
    start_time = DateTime()
    end_time = DateTime()

    attendees = g.List(_reltype('PubAttendeeSchema'))

    def __init__(self, model: models.Meeting):
        super().__init__(model)


class PubAttendeeSchema(g.ObjectType, EntityFields):
    meeting_id = ID()
    member_id = ID()

    meeting = g.Field(_reltype('PubMeetingSchema'))


class MyEligibleVoterSchema(g.ObjectType, EntityFields):
    voted = g.Boolean()
    election_id = ID()

    election = g.Field(_reltype('PubElectionSchema'))


class MyRole(g.ObjectType, EntityFields):
    committee_id = ID()
    name = g.NonNull(g.String)

    committee = g.Field(_reltype('PubCommitteeSchema'))

    def __init__(self, model: models.Role):
        self._model = model
        all_kwargs = {
            'id': model.id,
            'name': model.role,
        }
        super().__init__(**all_kwargs)

    def resolve_committee(self, args: dict, context: dict, info: ResolveInfo):
        return None \
            if self._model.committee is None \
            else PubCommitteeSchema(self._model.committee)


class MyUserSchema(g.ObjectType, EntityFields):
    first_name = g.String()
    last_name = g.String()
    name = g.String()
    email_address = g.String()
    biography = g.String()

    committees = g.List(_reltype('PubCommitteeSchema'))
    eligible_votes = g.List(_reltype('MyEligibleVoterSchema'))
    meetings_attended = g.List(_reltype('PubMeetingSchema'))
    roles = g.List(_reltype('MyRole'))

    def __init__(self, member: models.Member):
        self._model = member
        all_kwargs = {
            'id': member.id,
            'first_name': member.first_name,
            'last_name': member.last_name,
            'name': member.name,
            'email_address': member.email_address,
            'biography': member.biography,
        }
        super().__init__(**all_kwargs)

    def resolve_committees(self, args: dict, context: dict, info: ResolveInfo):
        return map(lambda x: PubCommitteeSchema(x), self._model.committees)

    def resolve_eligible_votes(self, args: dict, context: dict, info: ResolveInfo):
        return map(lambda x: MyEligibleVoterSchema(x), self._model.eligible_votes)

    def resolve_meetings_attended(self, args: dict, context: dict, info: ResolveInfo):
        return map(lambda x: PubMeetingSchema(x), self._model.meetings_attended)

    def resolve_roles(self, args: dict, context: dict, info: ResolveInfo):
        return map(lambda x: MyRole(x), self._model.roles)


class QuerySchema(g.ObjectType):
    all_attendees = g.List(AttendeeSchema)
    all_candidates = g.List(CandidateSchema)
    all_committees = g.List(CommitteeSchema)
    all_elections = g.List(ElectionSchema, id=g.Argument(ID))
    all_eligible_voters = g.List(EligibleVoterSchema, member_id=g.Argument(ID))
    all_meetings = g.List(MeetingSchema, id=g.Argument(ID))
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
        return MyUserSchema(requester)


def filters_for(model: Base, args: Dict[str, Any]):
    return [getattr(model, k) == v for k, v in args.items() if v is not None]


schema = g.Schema(query=QuerySchema)
