import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import create_engine, Column, String, ForeignKey, Date, Text, TIMESTAMP
from sqlalchemy.orm import relationship, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
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

    def new_user(log, pwd, email):
        user = User()
        user.username = log
        user.password_hash = generate_password_hash(pwd)
        user.email = email
        return user

    def check_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)
    
    def update(self, session, email = None):
        if email:
            self.email = email
        session.commit()

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

    def update(self, session, name = None, surname = None, birthdate = None, bio = None, phone = None):
        if name:
            self.first_name = name
        if surname:
            self.last_name = surname
        if birthdate:
            self.birthdate = birthdate
        if bio:
            self.bio = bio
        if phone:
            self.phone_number = phone

        if self not in session:
            session.add(self)

        session.commit()

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
