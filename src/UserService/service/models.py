import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import create_engine, Column, String, ForeignKey, Date, Text, TIMESTAMP
from sqlalchemy.orm import relationship, sessionmaker

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = relationship('UserProfile', uselist=False, back_populates='user')
    relations = relationship('UserRelations', foreign_keys='UserRelations.user_id', back_populates='user')

class UserProfile(db.Model):
    __tablename__ = 'user_profile'

    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('user.user_id'), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birthdate = Column(Date, nullable=True)
    bio = Column(Text, nullable=True)
    phone_number = Column(String(20), nullable=True)

    user = relationship('User', back_populates='profile')

class UserRelations(db.Model):
    __tablename__ = 'user_relations'

    user_id = Column(UUID(as_uuid=True), ForeignKey('user.user_id'), primary_key=True)
    related_user_id = Column(UUID(as_uuid=True), ForeignKey('user.user_id'), primary_key=True)
    relation_type = Column(String(20), nullable=False)
    relation_status = Column(String(20), nullable=False)
    started_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(Text, nullable=True)

    user = relationship('User', foreign_keys=[user_id], back_populates='relations')
    related_user = relationship('User', foreign_keys=[related_user_id])
