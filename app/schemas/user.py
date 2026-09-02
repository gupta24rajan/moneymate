from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


#Base Schema
class UserBase(BaseModel):
    username: str = Field(...,min_length=3, max_length=100)
    email: EmailStr = Field(..., description="Valid user email address")


#Request Schema (Registration / Signup)
class UserRegister(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="Plain text password")

# Request Schema (Update Profile)
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    email: Optional[EmailStr] = Field(None)


# Request Schema (Login)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Authentication Response Schemas (JWT Tokens)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None

# Response Schema (Public User Info - Never expose hashed_password!)
class UserResponse(UserBase):
    id: int
    created_at: datetime


   # Fixed typo: from_attributes instead of drom_attributes
    model_config = ConfigDict(drom_attributes=True)