from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import random


def generate_user_id():
    """Generate a 9-digit user ID"""
    user_id = random.randint(0, 999999999)
    return str(user_id).zfill(9)


class User(Base):
    __tablename__ = "users"
    
    id = Column(String(9), primary_key=True, default=lambda: str(generate_user_id()))
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user_details = relationship("UserDetails", back_populates="user", uselist=False, cascade="all, delete-orphan")
    personal_facts = relationship("PersonalFact", back_populates="user", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")


class UserDetails(Base):
    __tablename__ = "user_details"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(9), ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    bio = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="user_details")


class PersonalFact(Base):
    __tablename__ = "personal_facts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(9), ForeignKey("users.id"), nullable=False)
    fact_key = Column(String(100), nullable=False)  # e.g., "hobby", "birthday", "favorite_color"
    fact_value = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="personal_facts")


class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(9), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(100), index=True, nullable=False)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_history")
