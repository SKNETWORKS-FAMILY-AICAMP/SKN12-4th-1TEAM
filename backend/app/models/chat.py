import datetime 
from sqlalchemy import(
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    Enum as SQLAlchemyEnum,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from .db import Base
from .user import User

# 세션 데이터 테이블 정의
class Session(Base):
    """
    사용자와 챗봇 간의 개별 대화 세션을 관리하는 모델.
    """
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="세션 고유 ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), comment="사용자 ID") # 사용자 ID를 외래키로 참조하고, 사용자 삭제 시 세션도 함께 삭제되도록 설정
    session_id = Column(Integer, nullable=False, comment="사용자별 세션 순번")
    topic = Column(String(100), comment="대화 주제")
    summary = Column(Text, comment="대화 요약")
    status = Column(SQLAlchemyEnum('active', 'archived', 'error', name='session_status_enum'), default='active', comment="세션 상태")
    start_at = Column(DateTime, default=datetime.datetime.now, comment="세션 시작 시간")
    ended_at = Column(DateTime, nullable=True, comment="세션 종료 시간")
    
    # Session과 User 간의 N:1 관계 설정
    user = relationship("User", back_populates="sessions")
    # Session과 ChatLog 간의 1:N 관계 설정
    # 'logs'를 통해 세션에 속한 모든 채팅 로그에 접근
    logs = relationship("ChatLog", back_populates="session", cascade="all, delete-orphan")
    
    # user_id와 session_index 조합의 고유성을 보장
    __table_args__ = (UniqueConstraint('user_id', 'session_id', name='_user_session_uc'),)
    

class ChatLog(Base):
    """
    개별 채팅 메시지를 저장하는 모델
    활성 로그 테이블(chat-logs-active)에 매핑
    보관용 테이블(chat-logs-archived)에 매핑 
    """
    __tablename__ = "chat_logs_active"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="로그 고유 ID")
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, comment="세션 ID (FK)")
    
    sender = Column(SQLAlchemyEnum('user', 'bot', name='sender_enum'), nullable=False, comment="발신자 (사용자 또는 봇)")
    message = Column(Text, nullable=False, comment="메시지 내용")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, comment="전송 시간")

    # ChatLog와 Session 간의 N:1 관계 설정
    session = relationship("Session", back_populates="logs")
