from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import os
import requests

from database import get_db
from models import User
from core.security import get_current_user

router = APIRouter()

class AIChatRequest(BaseModel):
    message: str
    mode: str = "offline"  # offline, remote

class AIChatResponse(BaseModel):
    response: str
    source: str

OFFLINE_RESPONSES = {
    "center div": "Use Flexbox: `display: flex; justify-content: center; align-items: center;` on parent.",
    "reverse string": "JS: `s.split('').reverse().join('')` | Python: `s[::-1]`",
    "flexbox": "1D layouts: `justify-content` (main), `align-items` (cross axis)",
    "default": "Tell me more specifics about your question!"
}

@router.post("/chat", response_model=AIChatResponse)
async def ai_chat(request: AIChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """AI chat - offline rules or remote LLM proxy"""
    
    # Offline mode (default)
    if request.mode == "offline":
        key = next((k for k in OFFLINE_RESPONSES if k in request.message.lower()), "default")
        return AIChatResponse(
            response=OFFLINE_RESPONSES[key],
            source="offline"
        )
    
    # Remote mode (requires env vars)
    api_key = os.environ.get("AI_API_KEY")
    endpoint = os.environ.get("AI_ENDPOINT", "https://api.openai.com/v1/chat/completions")
    
    if not api_key:
        return AIChatResponse(
            response="Remote AI not configured. Set AI_API_KEY env var.",
            source="error"
        )
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": request.message}],
            "max_tokens": 200
        }
        
        resp = requests.post(endpoint, headers=headers, json=data, timeout=10)
        resp.raise_for_status()
        
        result = resp.json()
        message = result["choices"][0]["message"]["content"].strip()
        
        return AIChatResponse(response=message, source="remote")
    except Exception as e:
        return AIChatResponse(
            response=f"AI service error: {str(e)}",
            source="error"
        )

@router.post("/schedule")
async def generate_ai_schedule(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Generate AI study schedule (placeholder)"""
    return {
        "message": "AI Schedule generator coming soon - returns 30-day plan",
        "days": 30,
        "status": "planned"
    }
