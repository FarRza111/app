from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    is_admin: bool = False

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(UserBase):
    hashed_password: str
    is_admin: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    learning_streak: int = 0
    courses_enrolled: list[str] = []
    courses_completed: list[str] = []

class UserResponse(UserBase):
    is_admin: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None
    learning_streak: int = 0
    courses_enrolled: list[str] = []
    courses_completed: list[str] = []

    class Config:
        from_attributes = True
