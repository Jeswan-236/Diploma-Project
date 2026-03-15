from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class UserRole(str, Enum):
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.STUDENT)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    streaks = relationship("StreakDay", back_populates="user")
    topics = relationship("CalendarTopic", back_populates="user")
    practices = relationship("PracticeSubmission", back_populates="user")

class StreakDay(Base):
    __tablename__ = "streak_days"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    day_number = Column(Integer)  # 1-30
    status = Column(String, default="locked")  # locked, in-progress, completed
    completed_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="streaks")

class CalendarTopic(Base):
    __tablename__ = "calendar_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    month = Column(Integer)  # 0-11
    day = Column(Integer)
    subject = Column(String)
    topic = Column(String)
    time_slot = Column(String)  # morning, afternoon, evening
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="topics")

class PracticeSubmission(Base):
    __tablename__ = "practice_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    language = Column(String)
    prompt_title = Column(String)
    code = Column(Text)
    result = Column(String)  # pass/fail/feedback
    submitted_at = Column(DateTime, default=datetime.utcnow)
    updated_streak_day = Column(Integer, nullable=True)
    user = relationship("User", back_populates="practices")

# Pydantic schemas
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class StreakDayCreate(BaseModel):
    day_number: int
    status: str

class StreakDayResponse(BaseModel):
    id: int
    day_number: int
    status: str
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class CalendarTopicCreate(BaseModel):
    month: int
    day: int
    subject: str
    topic: str
    time_slot: str

class CalendarTopicResponse(BaseModel):
    id: int
    month: int
    day: int
    subject: str
    topic: str
    time_slot: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PracticeSubmissionCreate(BaseModel):
    language: str
    prompt_title: str
    code: str

class PracticeSubmissionResponse(BaseModel):
    id: int
    language: str
    prompt_title: str
    result: str
    submitted_at: datetime
    updated_streak_day: Optional[int]
    
    class Config:
        from_attributes = True
