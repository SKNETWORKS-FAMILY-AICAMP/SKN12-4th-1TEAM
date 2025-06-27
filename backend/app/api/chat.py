from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app.core.security import get_current_active_user
from app.models.db import get_db
from app.models.user import User as UserModel
from app.models.chat import Session as ChatSession, ChatLog
from app.schemas.chat import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatbotRequest,
    ChatbotResponse,
    GenerateTitleRequest,
    GenerateTitleResponse
)
from src.llm import get_chatbot

# 로깅 설정
logger = logging.getLogger(__name__)

router = APIRouter()

# 세션 관련 API 엔드포인트
@router.get("/sessions", response_model=List[SessionResponse])
async def get_user_sessions(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    현재 사용자의 모든 채팅 세션을 가져옵니다.
    """
    try:
        sessions = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id
        ).order_by(ChatSession.start_at.desc()).all()
        
        return sessions
    except Exception as e:
        logger.error(f"Error getting user sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="세션 목록을 가져오는 중 오류가 발생했습니다."
        )

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    새로운 채팅 세션을 생성합니다.
    """
    try:
        # 사용자별 세션 번호 계산
        last_session = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id
        ).order_by(ChatSession.session_id.desc()).first()
        
        next_session_id = 1
        if last_session:
            next_session_id = last_session.session_id + 1
            
        new_session = ChatSession(
            user_id=current_user.id,
            session_id=next_session_id,
            topic=session_data.topic,
            status=session_data.status,
            start_at=datetime.now()
        )
        
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        return new_session
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="세션 생성 중 오류가 발생했습니다."
        )

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    특정 채팅 세션의 정보를 가져옵니다.
    """
    try:
        session = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
            
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="세션 정보를 가져오는 중 오류가 발생했습니다."
        )

@router.put("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_data: SessionUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    특정 채팅 세션의 정보를 업데이트합니다.
    """
    try:
        session = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
            
        # 업데이트 가능한 필드만 수정
        if session_data.topic is not None:
            session.topic = session_data.topic
            
        if session_data.status is not None:
            session.status = session_data.status
            
            # 세션이 종료되면 종료 시간 설정
            if session_data.status == "archived":
                session.ended_at = datetime.now()
                
        if session_data.summary is not None:
            session.summary = session_data.summary
            
        db.commit()
        db.refresh(session)
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="세션 업데이트 중 오류가 발생했습니다."
        )

@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    특정 채팅 세션을 삭제합니다.
    """
    try:
        session = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
            
        db.delete(session)
        db.commit()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="세션 삭제 중 오류가 발생했습니다."
        )

# 메시지 관련 API 엔드포인트
@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_session_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    특정 채팅 세션의 모든 메시지를 가져옵니다.
    """
    try:
        # 세션 존재 확인
        session = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
            
        messages = db.query(ChatLog).filter(
            ChatLog.session_id == session.id  # session.id를 사용 (session.session_id가 아님)
        ).order_by(ChatLog.timestamp).all()
        
        return messages
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="메시지를 가져오는 중 오류가 발생했습니다."
        )

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    session_id: int,
    message_data: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    특정 채팅 세션에 새 메시지를 추가합니다.
    """
    try:
        # 세션 존재 확인
        session = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
            
        new_message = ChatLog(
            session_id=session.id,  # session.id를 사용 (session.session_id가 아님)
            sender=message_data.sender,
            message=message_data.message,
            timestamp=datetime.now()
        )
        
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        return new_message
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="메시지 생성 중 오류가 발생했습니다."
        )

# 메시지 기반 제목 생성 엔드포인트
@router.post("/generate-title", response_model=GenerateTitleResponse)
async def generate_title(
    request: GenerateTitleRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    첫 메시지 내용을 기반으로 세션 제목을 생성합니다.
    """
    try:
        # 세션 존재 확인
        session = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.session_id == request.session_id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션을 찾을 수 없습니다."
            )
        
        # 세션의 첫 메시지 가져오기
        first_message = db.query(ChatLog).filter(
            ChatLog.session_id == session.id,
            ChatLog.sender == "user"
        ).order_by(ChatLog.timestamp).first()
        
        if not first_message:
            return {"title": "새 채팅"}
        
        # LLM을 사용하여 제목 생성
        chatbot = get_chatbot()
        title = chatbot.generate_title(first_message.message)
        
        # 세션 제목 업데이트
        session.topic = title
        db.commit()
        
        return {"title": title}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error generating title: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="제목 생성 중 오류가 발생했습니다."
        ) 