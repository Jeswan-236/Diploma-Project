from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import and_

from datetime import datetime
from database import get_db
from models import CalendarTopic, CalendarTopicCreate, CalendarTopicResponse, User
from core.security import get_current_user

router = APIRouter()

@router.get("/month/{month}", response_model=List[CalendarTopicResponse])
def get_month_topics(month: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all topics for a specific month (0-11)"""
    if month < 0 or month > 11:
        raise HTTPException(status_code=400, detail="Month must be 0-11")
    
    topics = db.query(CalendarTopic).filter(
        and_(
            CalendarTopic.user_id == current_user.id,
            CalendarTopic.month == month
        )
    ).order_by(CalendarTopic.day).all()
    return topics

@router.post("/", response_model=CalendarTopicResponse)
def create_topic(topic: CalendarTopicCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create or update calendar topic for specific day"""
    # Validate inputs
    if topic.month < 0 or topic.month > 11 or topic.day < 1 or topic.day > 31:
        raise HTTPException(status_code=400, detail="Invalid month/day")
    
    existing = db.query(CalendarTopic).filter(
        and_(
            CalendarTopic.user_id == current_user.id,
            CalendarTopic.month == topic.month,
            CalendarTopic.day == topic.day
        )
    ).first()
    
    if existing:
        # Update
        existing.subject = topic.subject
        existing.topic = topic.topic
        existing.time_slot = topic.time_slot
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new
    db_topic = CalendarTopic(
        user_id=current_user.id,
        month=topic.month,
        day=topic.day,
        subject=topic.subject,
        topic=topic.topic,
        time_slot=topic.time_slot
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic

@router.delete("/month/{month}/day/{day}")
def delete_topic(month: int, day: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Delete topic for specific day"""
    topic = db.query(CalendarTopic).filter(
        and_(
            CalendarTopic.user_id == current_user.id,
            CalendarTopic.month == month,
            CalendarTopic.day == day
        )
    ).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    db.delete(topic)
    db.commit()
    return {"message": "Topic deleted"}

@router.get("/today")
def get_todays_topic(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get topic for today (if exists)"""
    from datetime import datetime
    now = datetime.utcnow()
    month = now.month - 1  # 0-indexed
    day = now.day
    
    topic = db.query(CalendarTopic).filter(
        and_(
            CalendarTopic.user_id == current_user.id,
            CalendarTopic.month == month,
            CalendarTopic.day == day
        )
    ).first()
    
    if topic:
        return {
            "month": month,
            "day": day,
            "subject": topic.subject,
            "topic": topic.topic,
            "time_slot": topic.time_slot
        }
    return {"message": "No topic scheduled for today"}
