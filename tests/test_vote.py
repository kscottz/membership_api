from membership.util.vote import Election


def test_transfer():
    candidates = ['Alice', 'Bob', 'Carol']
    votes = []
    votes.extend([['Carol', 'Bob', 'Alice']]*20)
    votes.extend([['Alice', 'Carol', 'Bob']]*5)
    election = Election(candidates, 2, votes)
    election.hold_election()
    assert election.winners == ['Carol', 'Bob']


def test_tie_break():
    candidates = ['Alice', 'Bob', 'Carol', 'Doug']
    votes = []
    votes.extend([['Carol', 'Bob', 'Alice', 'Doug']]*10)
    votes.extend([['Bob', 'Carol', 'Alice', 'Doug']]*4)
    votes.extend([['Doug', 'Carol', 'Alice', 'Bob']]*1)
    votes.extend([['Doug', 'Carol', 'Bob', 'Alice']]*1)
    votes.extend([['Alice', 'Carol', 'Bob', 'Doug']]*6)
    election = Election(candidates, 2, votes)
    election.hold_election()
    assert election.winners == ['Carol', 'Alice']