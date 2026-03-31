from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Used for user registration
class UserCreate(BaseModel):
    username: str
    password: str

# Used for user login (can reuse UserCreate, but kept separate for clarity)
class UserLogin(BaseModel):
    username: str
    password: str

# Used for returning JWT token
class Token(BaseModel):
    access_token: str
    token_type: str

# Used for returning User information (avoid returning password)
class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    # Tell Pydantic to read data even if it is not a dict, but an ORM model
    model_config = ConfigDict(from_attributes=True)
