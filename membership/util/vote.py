import random
from decimal import Decimal, getcontext
from typing import Dict, Generic, List, Set, TypeVar

ZERO = Decimal('0.00000')
ONE = Decimal('1.00000')

T = TypeVar('T')


class Vote(Generic[T]):
    def __init__(self, choices: List[T]):
        self.weight: Decimal = ONE
        self.choice_stack: List[T] = list(reversed(choices))

    def transfer(self, transfer_weight: Decimal, remaining_candidates: Set[T]) -> None:
        self.weight *= transfer_weight
        self.choice_stack.pop()
        while self.choice_stack and self.choice_stack[-1] not in remaining_candidates:
            self.choice_stack.pop()


class CandidateVotes(Generic[T]):
    def __init__(self, candidate: T):
        self.candidate: T = candidate
        self.total: Decimal = ZERO
        self.transfer_total: Decimal = ZERO
        self.votes: List[Vote[T]] = []


class STVElection(Generic[T]):
    def __init__(self, candidates: List[T], num_winners: int, choices_list: List[List[T]]):
        self.votes: List[Vote[T]] = [Vote(choices) for choices in choices_list]
        self.winners: List[T] = []
        self.remaining_candidates: Set[T] = set(candidates)
        self.num_winners: int = num_winners
        self.previous_rounds: List[Dict[CandidateVotes[T], dict]] = []

        self.quota = int(len(self.votes) / (self.num_winners + 1)) + 1
        getcontext().prec = 5

    def hold_election(self) -> List[T]:
        while len(self.winners) < self.num_winners and len(self.remaining_candidates) > 0:
            self.count_votes()
        return self.winners

    def count_votes(self) -> None:
        candidate_votes: Dict[T, CandidateVotes[T]] = {candidate: CandidateVotes(candidate) for candidate in self.remaining_candidates}
        for vote in self.votes:  # type: Vote[T]
            if len(vote.choice_stack) > 0 and vote.weight > ZERO:
                cv = candidate_votes[vote.choice_stack[-1]]
                cv.total += vote.weight
                # If this is a transfer vote, record it as such
                if vote.weight < ONE:
                    cv.transfer_total += vote.weight
                cv.votes.append(vote)
        self.previous_rounds.append(
            {
                cv.candidate: {'total_votes': cv.total, 'total_transfer_votes': cv.transfer_total}
                for cv in candidate_votes.values()
            }
        )

        result = list(candidate_votes.values())
        result.sort(key=lambda x: x.total, reverse=True)
        if result[0].total >= self.quota or len(self.remaining_candidates) <= self.num_winners - len(self.winners):
            i = 0
            round_winners = []
            while i < len(result) and result[i].total == result[0].total:
                round_winners.append(result[i])
                i += 1
            winner = self.break_tie(round_winners, len(self.previous_rounds) - 1, True)
            self.winners.append(winner.candidate)
            self.remaining_candidates.remove(winner.candidate)
            if winner.total > self.quota:
                transfer_weight = Decimal((winner.total - self.quota) / winner.total).quantize(ZERO)
            else:
                transfer_weight = ZERO
            for vote in winner.votes:
                vote.transfer(transfer_weight, self.remaining_candidates)
        else:
            i = len(result) - 1
            round_losers = []
            while i >= 0 and result[i].total == result[-1].total:
                round_losers.append(result[i])
                i -= 1
            loser = self.break_tie(round_losers, len(self.previous_rounds) - 1, False)
            self.remaining_candidates.remove(loser.candidate)
            for vote in loser.votes:
                vote.transfer(ONE, self.remaining_candidates)

    def break_tie(self, round_winners: List[CandidateVotes[T]], voting_round: int, win: bool) -> CandidateVotes[T]:
        multiplier = 1 if win else -1
        if len(round_winners) == 1:
            return round_winners[0]
        if voting_round == 0:
            return random.choice(round_winners)
        max_vote = None
        next_round_winners = []
        for winner in round_winners:
            total = multiplier * self.previous_rounds[voting_round - 1][winner.candidate]['total_votes']
            if max_vote is None or total > max_vote:
                next_round_winners = [winner]
                max_vote = total
            elif total == max_vote:
                next_round_winners.append(winner)
        return self.break_tie(next_round_winners, voting_round - 1, win)
