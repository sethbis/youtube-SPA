from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserSummary(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserOut(UserBase):
    id: int
    created_at: Optional[datetime] = None
    video_count: Optional[int] = 0

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class VideoBase(BaseModel):
    title: str
    description: Optional[str] = None

class VideoCreate(VideoBase):
    pass

class VideoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class VideoOut(VideoBase):
    id: int
    video_url: str
    thumbnail_url: str
    views: int
    user_id: int
    created_at: datetime
    owner: Optional[UserSummary] = None

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    pass

class CommentOut(CommentBase):
    id: int
    user_id: int
    video_id: int
    created_at: datetime
    author: Optional[UserSummary] = None

    class Config:
        from_attributes = True
