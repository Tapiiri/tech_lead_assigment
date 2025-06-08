from pydantic import BaseModel, HttpUrl, EmailStr
from datetime import datetime


class MemberBase(BaseModel):
    first_name: str
    last_name: str
    login: str
    avatar_url: HttpUrl
    followers: int
    following: int
    title: str
    email: EmailStr


class MemberCreate(MemberBase):
    pass


class MemberRead(MemberBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
