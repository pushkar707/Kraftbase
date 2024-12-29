from sqlalchemy import String, Integer, Column, JSON, ForeignKey, DateTime
from db import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    forms = relationship('Form', back_populates='user')


class Form(Base):
    __tablename__ = 'forms'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    fields = Column(JSON)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='forms')
    submissions = relationship('Submission', back_populates='form')


class Submission(Base):
    __tablename__ = 'submissions'

    submission_id = Column(Integer, primary_key=True, index=True)
    data = Column(JSON)
    form_id = Column(Integer, ForeignKey('forms.id'))
    submitted_at = Column(DateTime, default=datetime.now())

    form = relationship('Form', back_populates='submissions')
