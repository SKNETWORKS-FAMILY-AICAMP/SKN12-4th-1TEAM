from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 세션 관련 스키마
class SessionBase(BaseModel):
    """
    세션의 기본 스키마
    """
    topic: Optional[str] = None
    status: str = "active"
    summary: Optional[str] = None

class SessionCreate(SessionBase):
    """
    세션 생성 요청 스키마
    """
    pass

class SessionUpdate(BaseModel):
    """
    세션 업데이트 요청 스키마
    """
    topic: Optional[str] = None
    status: Optional[str] = None
    summary: Optional[str] = None

class SessionResponse(SessionBase):
    """
    세션 응답 스키마
    """
    session_id: int
    user_id: int
    start_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 메시지 관련 스키마
class ChatMessageBase(BaseModel):
    """
    채팅 메시지의 기본 스키마
    """
    message: str
    sender: str  # 'user' 또는 'bot'

class ChatMessageCreate(ChatMessageBase):
    """
    채팅 메시지 생성 요청 스키마
    """
    pass

class ChatMessageResponse(ChatMessageBase):
    """
    채팅 메시지 응답 스키마
    """
    id: int
    session_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# 챗봇 요청/응답 스키마
class ChatbotRequest(BaseModel):
    """
    챗봇에 대한 요청 스키마
    """
    query: str
    session_id: Optional[int] = None

class ChatbotResponse(BaseModel):
    """
    챗봇의 응답 스키마
    """
    response: str
    session_id: Optional[int] = None

# 제목 생성 요청/응답 스키마
class GenerateTitleRequest(BaseModel):
    """
    제목 생성 요청 스키마
    """
    session_id: int

class GenerateTitleResponse(BaseModel):
    """
    제목 생성 응답 스키마
    """
    title: str 