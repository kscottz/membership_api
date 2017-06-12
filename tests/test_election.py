from membership.database.models import Candidate, Member, Election, Vote, Ranking
from membership.database.base import engine, metadata, Base, Session
from membership.web.elections import hold_election
from random import shuffle


class TestElection:

    @classmethod
    def setup_class(cls):
        metadata.create_all(engine)


    @classmethod
    def teardown_class(cls):
        metadata.drop_all(engine)

    def test_election(self):
        num_votes = 500
        session = Session()
        a = Member(first_name='A', last_name='B')
        session.add(a)
        c = Member(first_name='C', last_name='D')
        session.add(c)
        e = Member(first_name='E', last_name='F')
        candidates = []
        for member in [a, c, e]:
            cand = Candidate()
            cand.member = member
            candidates.append(cand)
        session.add(e)
        election = Election(name='Test', number_winners=2)
        election.candidates.extend(candidates)
        session.add(election)

        for i in range(0, num_votes):
            shuffle(candidates)
            vote = Vote()
            election.votes.append(vote)
            for j, cand in enumerate(candidates):
                rank = Ranking(rank=i)
                rank.candidate = cand
                vote.ranking.append(rank)
        session.commit()
        session.close()

        session = Session()
        election = session.query(Election).filter_by(name='Test').one()
        results = hold_election(election)
        assert len(results.winners) == 2
        assert len(results.votes) == num_votes
