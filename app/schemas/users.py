from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    email: EmailStr
    full_name: str | None = Field(default=None, max_length=200)
    password: str = Field(min_length=8, max_length=128)
