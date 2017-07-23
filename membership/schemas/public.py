from graphene.types.datetime import DateTime
from sqlalchemy.orm.query import Query

from .admin import *
from .common import *


# API View Models

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

    @Schema.resolver
    def resolve_all_attendees(self, env: ResolveEnv):
        query: Query = AttendeeSchema.get_query(env.context)
        return query.all()

    @Schema.resolver
    def resolve_all_candidates(self, env: ResolveEnv):
        query: Query = CandidateSchema.get_query(env.context)
        return query.all()

    @Schema.resolver
    def resolve_all_committees(self, env: ResolveEnv):
        query: Query = CommitteeSchema.get_query(env.context)
        return query.all()

    @Schema.resolver
    def resolve_all_elections(self, env: ResolveEnv):
        query: Query = ElectionSchema.get_query(env.context)
        return query.all()

    @Schema.resolver
    def resolve_all_eligible_voters(self, env: ResolveEnv):
        query: Query = EligibleVoterSchema.get_query(env.context)
        return query.all()

    @Schema.resolver
    def resolve_all_meetings(self, env: ResolveEnv):
        query: Query = MeetingSchema.get_query(env.context)
        return query.all()

    @Schema.resolver
    def resolve_all_members(self, env: ResolveEnv):
        requester: Member = env.context['requester']
        query: Query = MemberSchema.get_query(env.context)
        filter_id = env.args.get('id')
        if requester.is_admin():
            query = query.filter(Member.id == filter_id)
            return query.all()
        else:
            return [requester] if not filter_id else \
                requester if requester.id == filter_id else []

    @Schema.resolver
    def resolve_public_elections(self, env: ResolveEnv):
        query: Query = ElectionSchema.get_query(env.context)
        all: List[Election] = query.all()
        return all

    @Schema.resolver
    def resolve_all_rankings(self, env: ResolveEnv):
        query: Query = RankingSchema.get_query(env.context)
        return query.all()

    @Schema.resolver
    def resolve_all_roles(self, env: ResolveEnv):
        query: Query = RoleSchema.get_query(env.context)
        return query.all()

    @Schema.resolver
    def resolve_all_votes(self, env: ResolveEnv):
        query: Query = VoteSchema.get_query(env.context)
        return query.all()

    @Schema.resolver
    def resolve_my_user(self, env: ResolveEnv):
        requester: Member = env.context['requester']
        x = MyUserSchema(requester)
        return x
