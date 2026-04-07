import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

# Load env variables from .env in the same directory
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

# Settings from .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 week

# Initialize Supabase
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials not found. Please ensure .env is properly set up.")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="SkillStalker API")

# Enable CORS for the frontend portal
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# --- Pydantic Models ---
class RegisterRequest(BaseModel):
    fullname: str
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserProfile(BaseModel):
    id: int
    fullname: str
    username: str
    email: str
    is_admin: bool

# --- Password & JWT Utilities ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependency: Current User ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    response = supabase.table("users").select("*").eq("username", username).execute()
    if not response.data:
        raise credentials_exception
        
    return response.data[0]

# --- Endpoints ---

@app.post("/api/auth/register")
async def register_user(user: RegisterRequest):
    existing_user_resp = supabase.table("users").select("id").eq("username", user.username).execute()
    if existing_user_resp.data:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    existing_email_resp = supabase.table("users").select("id").eq("email", user.email).execute()
    if existing_email_resp.data:
        raise HTTPException(status_code=400, detail="Email already registered")

    is_admin = (user.username == "skillstalkeradmin")

    new_user = {
        "fullname": user.fullname,
        "username": user.username,
        "email": user.email,
        "password_hash": get_password_hash(user.password),
        "is_admin": is_admin
    }
    
    insert_resp = supabase.table("users").insert(new_user).execute()
    if not insert_resp.data:
        raise HTTPException(status_code=500, detail="Failed to create user")
        
    return {"message": "User registered successfully"}


@app.post("/api/auth/login")
async def login_user(user: LoginRequest):
    response = supabase.table("users").select("*").eq("username", user.username).execute()
    
    if not response.data:
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    db_user = response.data[0]
    if not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    access_token = create_access_token(data={"sub": db_user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=UserProfile)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserProfile(
        id=current_user["id"],
        fullname=current_user["fullname"],
        username=current_user["username"],
        email=current_user["email"],
        is_admin=current_user.get("is_admin", False)
    )


@app.get("/api/users")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized. Admins only.")
        
    response = supabase.table("users").select("id, fullname, username, email, is_admin").execute()
    return {"users": response.data}


@app.get("/")
def read_root():
    return {"status": "online", "message": "SkillStalker API is running"}
