from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta

# Import from our application modules
from database import engine, Base, get_db
from models import User
from schemas import UserCreate, UserLogin, Token, UserResponse
from auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Initialize database tables
# In production, you would typically use Alembic for migrations instead
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SkillStalker API",
    description="Backend API for the SkillStalker student mental health platform",
    version="0.1.0"
)

# Configure CORS for frontend communication
# Update allow_origins with your frontend URL in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all REST methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with a unique username and password.
    """
    # Check if username already exists in the database
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash the plain-text password securely
    hashed_password = get_password_hash(user.password)
    
    # Create the User model instance
    new_user = User(username=user.username, password_hash=hashed_password)
    
    # Save to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/api/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.
    """
    # Retrieve user from the database
    db_user = db.query(User).filter(User.username == user.username).first()
    
    # Verify user exists and password is correct
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate JWT access token upon successful verification
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
