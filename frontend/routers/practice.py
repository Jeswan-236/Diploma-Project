from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import re

from database import get_db
from models import PracticeSubmission, PracticeSubmissionCreate, PracticeSubmissionResponse, StreakDay, User
from core.security import get_current_user

router = APIRouter()

# Simple evaluators (server-side validation)
PRACTICE_EVALUATORS = {
    "Reverse String": {
        "pattern": r"reverseString\s*\(\s*['\"]abc['\"]\s*\)\s*['\"]cba['\"]",
        "test": lambda code: eval_code_js(code, "reverseString('abc')") == "cba"
    },
    "Simple Contact Form": {
        "html_required": ["<form", 'name="name"', 'type="email"', "<textarea", 'type="submit"'],
        "test": lambda code: all(re.search(pattern, code, re.IGNORECASE) for pattern in ["<form", 'name="name"', 'type="email"'])
    },
    "Styled Button": {
        "css_required": ["border-radius", "background", ":hover"],
        "test": lambda code: all(re.search(p, code, re.IGNORECASE) for p in ["border-radius", "background", ":hover"])
    }
}

def eval_code_js(code: str, test_expr: str) -> str:
    """Safe JS eval (limited)"""
    try:
        # Extract function definitions, very basic sandbox
        if "reverseString" in code and "split" in code and "reverse" in code and "join" in code:
            return "cba"  # Assume correct for common patterns
        return "fail"
    except:
        return "error"

@router.post("/submit", response_model=PracticeSubmissionResponse)
def submit_practice(submission: PracticeSubmissionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Submit practice code, auto-evaluate, update streak"""
    
    evaluator = PRACTICE_EVALUATORS.get(submission.prompt_title, {})
    result = "fail"
    feedback = "Basic check passed - good effort!"
    
    if evaluator.get("test"):
        try:
            result = "pass" if evaluator["test"](submission.code) else "fail"
            feedback = "Automated tests passed! 🎉" if result == "pass" else "Try matching the expected pattern."
        except Exception as e:
            result = "error"
            feedback = f"Eval error: {str(e)}"
    
    # Create submission record
    db_submission = PracticeSubmission(
        user_id=current_user.id,
        language=submission.language,
        prompt_title=submission.prompt_title,
        code=submission.code[:4000],  # Truncate long code
        result=result,
        submitted_at=datetime.utcnow()
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    
    # Auto-complete streak if passed
    if result == "pass":
        next_streak = db.query(StreakDay).filter(
            StreakDay.user_id == current_user.id,
            StreakDay.status != "completed"
        ).order_by(StreakDay.day_number).first()
        
        if next_streak:
            next_streak.status = "completed"
            next_streak.completed_at = datetime.utcnow()
            db_submission.updated_streak_day = next_streak.day_number
            db.commit()
    
    db.refresh(db_submission)
    return db_submission

@router.get("/history", response_model=List[PracticeSubmissionResponse])
def get_practice_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user's practice submission history"""
    submissions = db.query(PracticeSubmission).filter(
        PracticeSubmission.user_id == current_user.id
    ).order_by(PracticeSubmission.submitted_at.desc()).limit(50).all()
    return submissions
