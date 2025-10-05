from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=200)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    hashed_password: str | None = None


class User(UserBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserInDB(User):
    hashed_password: str
