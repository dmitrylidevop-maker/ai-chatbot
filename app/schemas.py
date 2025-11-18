from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# User Details Schemas
class UserDetailsBase(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


class UserDetailsCreate(UserDetailsBase):
    pass


class UserDetailsUpdate(UserDetailsBase):
    pass


class UserDetailsResponse(UserDetailsBase):
    id: int
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Personal Facts Schemas
class PersonalFactBase(BaseModel):
    fact_key: str = Field(..., max_length=100)
    fact_value: str


class PersonalFactCreate(PersonalFactBase):
    pass


class PersonalFactUpdate(BaseModel):
    fact_value: str


class PersonalFactResponse(PersonalFactBase):
    id: int
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Chat Schemas
class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    role: str
    message: str
    timestamp: datetime


class ChatHistoryResponse(BaseModel):
    id: int
    session_id: str
    role: str
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
