import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.user import router as user_router
from app.api.chat import router as chat_router
from app.schemas.chat import ChatbotRequest, ChatbotResponse
from app.models.db import get_db
from app.models.chat import Session as ChatSession, ChatLog
from app.core.security import get_current_active_user
from sqlalchemy.orm import Session
from src.llm import process_query
from datetime import datetime

# Load environment variables from all possible locations
env_paths = [
    Path(__file__).resolve().parent / '.env',
    Path(__file__).resolve().parent.parent / '.env',
    Path.cwd() / '.env'
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        break

# FastAPI app creation
app = FastAPI(
    title="Pet Travel API",
    description="반려동물 여행 정보 제공 및 채팅 API",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost:3000",  # React development server
    "http://127.0.0.1:3000",
    os.getenv("FRONTEND_URL", "http://localhost:3000")  # Production URL
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600
)

# Router registration
app.include_router(user_router, prefix="/api", tags=["users"])
app.include_router(chat_router, prefix="/api", tags=["chat"])

@app.post("/api/chat", response_model=ChatbotResponse, tags=["chatbot"])
async def chat(
    request: ChatbotRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    반려동물 여행 챗봇 API
    
    사용자의 질문을 처리하고 응답을 반환합니다.
    세션 ID가 제공되면 해당 세션에 메시지를 저장합니다.
    """
    # 세션 확인
    if request.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.user_id == current_user.id,
            ChatSession.session_id == request.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 챗봇 응답 생성 - 세션 ID 전달
    response_text = process_query(request.query, request.session_id)
    
    # 세션이 있으면 봇 메시지 저장
    if request.session_id:
        bot_message = ChatLog(
            session_id=session.id,  # session.id를 사용 (session.session_id가 아님)
            sender="bot",
            message=response_text,
            timestamp=datetime.now()
        )
        
        db.add(bot_message)
        db.commit()
    
    return ChatbotResponse(
        response=response_text,
        session_id=request.session_id
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to Pet Travel API"}