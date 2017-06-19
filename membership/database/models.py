# coding: utf-8
from datetime import datetime
from membership.database.base import Base
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer, Float, Numeric, \
    String, Time
from sqlalchemy.orm import backref, reconstructor, relationship
from sqlalchemy.schema import UniqueConstraint


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, unique=True)
    first_name = Column(String(45))
    last_name = Column(String(45))
    email_address = Column(String(254), unique=True)
    biography = Column(String(10000))

    @property
    def name(self):
        n = ''
        if self.first_name:
            n = self.first_name
        if self.last_name:
            n += ' ' + self.last_name
        return n


class Committee(Base):
    __tablename__ = 'committees'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(45))


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, unique=True)
    committee_id = Column(ForeignKey('committees.id'))
    member_id = Column(ForeignKey('members.id'))
    role = Column(String(45))

    committee = relationship(Committee)
    member = relationship(Member, backref='roles')


class Meeting(Base):
    __tablename__ = 'meetings'

    id = Column(Integer, primary_key=True, unique=True)
    short_id = Column(Integer, nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    committee_id = Column(ForeignKey('committees.id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime)


class Attendee(Base):
    __tablename__ = 'attendees'

    id = Column(Integer, primary_key=True, unique=True)
    meeting_id = Column(ForeignKey('meetings.id'))
    member_id = Column(ForeignKey('members.id'))

    member = relationship(Member, backref='meetings_attended')
    meeting = relationship(Meeting, backref='attendees')


class Election(Base):
    __tablename__ = 'elections'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(45), nullable=False)
    status = Column(String(45), nullable=False, default='draft')
    number_winners = Column(Integer)


class Candidate(Base):
    __tablename__ = 'candidates'

    id = Column(Integer, primary_key=True, unique=True)
    member_id = Column(ForeignKey('members.id'))
    election_id = Column(ForeignKey('elections.id'))

    member = relationship(Member)
    election = relationship(Election, backref='candidates')


class Vote(Base):
    __tablename__ = 'votes'
    __table_args__ = (UniqueConstraint('vote_key', 'election_id'),)

    id = Column(Integer, primary_key=True, unique=True)
    vote_key = Column(Integer)
    election_id = Column(ForeignKey('elections.id'))

    election = relationship(Election, backref='votes')


class Ranking(Base):
    __tablename__ = 'rankings'

    id = Column(Integer, primary_key=True, unique=True)
    vote_id = Column(ForeignKey('votes.id'))
    rank = Column(Integer)
    candidate_id = Column(ForeignKey('candidates.id'))

    vote = relationship(Vote, backref=backref('ranking', order_by="Ranking.rank"))
    candidate = relationship(Candidate)


class EligibleVoter(Base):
    __tablename__ = 'eligible_voters'

    id = Column(Integer, primary_key=True, unique=True)
    member_id = Column(ForeignKey('members.id'))
    voted = Column(Boolean)
    election_id = Column(ForeignKey('elections.id'))

    member = relationship(Member, backref='eligible_votes')
    election = relationship(Election, backref='voters')
