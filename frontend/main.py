import os
os.chdir(os.path.dirname(__file__))
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base, get_db
from models import User, StreakDay, CalendarTopic, PracticeSubmission
from routers.auth import router as auth_router
from routers.streak import router as streak_router
from routers.calendar import router as calendar_router
from routers.practice import router as practice_router
from routers.ai import router as ai_router
from core.security import oauth2_scheme, get_current_user

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Skill Stalker Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(streak_router, prefix="/streak", tags=["streak"])
app.include_router(calendar_router, prefix="/calendar", tags=["calendar"])
app.include_router(practice_router, prefix="/practice", tags=["practice"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])

@app.get("/")
async def root():
    return {"message": "Skill Stalker Backend Ready! http://localhost:8000/docs"}

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
