from sqlalchemy import String, Integer, Column, JSON, ForeignKey
from db import Base
from sqlalchemy.orm import relationship


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
