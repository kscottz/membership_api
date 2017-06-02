# coding: utf-8
from datetime import datetime
from membership.database.base import Base
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Integer, Float, Numeric, \
    String, Time
from sqlalchemy.orm import backref, reconstructor, relationship


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, unique=True)
    first_name = Column(String(45))
    last_name = Column(String(45))
    email_address = Column(String(254), unique=True)


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