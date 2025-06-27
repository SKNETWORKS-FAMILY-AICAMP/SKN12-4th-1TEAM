from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# -------------------------------
# Token 관련 스키마
# -------------------------------

class Token(BaseModel):
    """
    클라이언트에게 전달될 JWT 토큰 스키마
    """
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str
    user: Optional[dict] = None  # 사용자 정보를 포함할 수 있도록 추가


class TokenData(BaseModel):
    """
    토큰 디코딩 후 얻게 되는 데이터 스키마
    """
    username: Optional[str] = None

# -------------------------------
# ChatMessage 관련 스키마
# -------------------------------

class ChatMessageBase(BaseModel):
    content: str


class ChatMessageCreate(ChatMessageBase):
    """
    대화 메시지 생성 요청
    """
    pass


class ChatMessage(ChatMessageBase):
    """
    대화 메시지 응답
    """
    id: int
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True

# -------------------------------
# User 관련 스키마
# -------------------------------

class UserBase(BaseModel):
    """
    사용자 정보의 기본 스키마
    """
    email: EmailStr
    username: str  # 사용자 아이디
    nickname: str  # 사용자 닉네임


class UserCreate(UserBase):
    """
    사용자 생성 시 사용되는 스키마
    """
    password: str


class UserLogin(BaseModel):
    """
    로그인 요청 스키마 (email + password)
    """
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """
    유저 정보 수정 (선택적)
    """
    nickname: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    """
    사용자 정보 반환 시 사용되는 스키마
    """
    id: int
    is_active: bool
    is_superuser: bool = False
    messages: List[ChatMessage] = []

    class Config:
        from_attributes = True