from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import and_
from datetime import datetime

from database import get_db
from models import StreakDay, StreakDayCreate, StreakDayResponse, User
from core.security import get_current_user

router = APIRouter()

@router.get("/", response_model=List[StreakDayResponse])
def get_streak_days(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's 30-day streak"""
    days = db.query(StreakDay).filter(StreakDay.user_id == current_user.id).order_by(StreakDay.day_number).all()
    return days

@router.post("/", response_model=StreakDayResponse)
def create_streak_day(day: StreakDayCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Create or update streak day"""
    existing = db.query(StreakDay).filter(
        and_(
            StreakDay.user_id == current_user.id,
            StreakDay.day_number == day.day_number
        )
    ).first()
    
    if existing:
        existing.status = day.status
        if day.status == "completed":
            existing.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing
    
    db_streak = StreakDay(
        user_id=current_user.id,
        day_number=day.day_number,
        status=day.status
    )
    db.add(db_streak)
    db.commit()
    db.refresh(db_streak)
    return db_streak

@router.get("/current-streak")
def get_current_streak(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current consecutive streak count"""
    days = db.query(StreakDay).filter(
        StreakDay.user_id == current_user.id,
        StreakDay.status == "completed"
    ).order_by(StreakDay.day_number).all()
    
    streak = 0
    for day in days:
        if day.day_number == streak + 1:
            streak += 1
        else:
            break
    
    return {"current_streak": streak, "total_completed": len(days)}

@router.post("/complete-next")
def complete_next_streak_day(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Complete the next incomplete streak day"""
    # Find next incomplete day (1-30)
    for day_num in range(1, 31):
        existing = db.query(StreakDay).filter(
            and_(
                StreakDay.user_id == current_user.id,
                StreakDay.day_number == day_num
            )
        ).first()
        
        if not existing or existing.status != "completed":
            if existing:
                existing.status = "completed"
                existing.completed_at = datetime.utcnow()
            else:
                new_day = StreakDay(
                    user_id=current_user.id,
                    day_number=day_num,
                    status="completed"
                )
                db.add(new_day)
            
            db.commit()
            return {"completed_day": day_num}
    
    raise HTTPException(status_code=400, detail="All 30 days completed!")
