import datetime 
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, index=True)
    nickname = Column(String(20), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # 채팅 메시지 관계 설정
    messages = relationship("ChatMessage", back_populates="user")
    # 세션 관계 설정
    sessions = relationship("Session", back_populates="user")
    
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(Integer, ForeignKey("users.id"))

    # 사용자 관계 설정
    user = relationship("User", back_populates="messages")