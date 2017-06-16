from membership.database.models import Candidate, Member, Election, Vote, Ranking
from membership.database.base import engine, metadata, Base, Session
from membership.web.elections import hold_election
from random import shuffle
from hypothesis.strategies import data
from hypothesis import given
import hypothesis.strategies as st


class TestElection:
    @classmethod
    def setup_class(cls):
        metadata.create_all(engine)

    @classmethod
    def teardown_class(cls):
        metadata.drop_all(engine)

    @given(data())
    def test_election_prob(self, data):
        # Set up the SQLAlchemy session
        metadata.drop_all(engine)
        metadata.create_all(engine)
        session = Session()

        # Randomly generate parameters
        num_votes = data.draw(st.integers(min_value=0, max_value=500))
        num_candidates = data.draw(st.integers(min_value=1, max_value=10))
        num_winners = data.draw(st.integers(min_value=1, max_value=num_candidates))

        # Create candidates as members and add them to the DB
        candidate_members = [Member(first_name=str(i),
                                    last_name=str(i)) for i in range(num_candidates)]
        session.add_all(candidate_members)
        # Create candidates as candidates and add them to the DB
        candidates = [Candidate(member=member) for member in candidate_members]
        session.add_all(candidates)
        # Create the election and add to DB
        election = Election(name='Test2', number_winners=num_winners)
        election.candidates.extend(candidates)
        session.add(election)

        # Generate votes for the candidates
        for i in range(num_votes):
            shuffle(candidates)
            vote = Vote()
            election.votes.append(vote)
            for j, cand in enumerate(candidates):
                rank = Ranking(rank=i)
                rank.candidate = cand
                vote.ranking.append(rank)

        # Commit everything to DB
        session.commit()
        session.close()

        # Get the election back from the DB, hold the election
        new_session = Session()
        election = new_session.query(Election).filter_by(name='Test2').one()
        results = hold_election(election)

        # Check the results
        assert len(results.winners) == num_winners
        assert len(results.votes) == num_votes

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
