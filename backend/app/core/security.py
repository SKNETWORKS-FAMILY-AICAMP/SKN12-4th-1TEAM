import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError as JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.db import get_db
from app.models.user import User as UserModel
from app.schemas.user import User as UserSchema
from dotenv import load_dotenv

load_dotenv()

# 로거 설정
logger = logging.getLogger(__name__)

# --- 보안 설정 ---
# 서버 재시작 후에도 토큰이 유효하도록 고정된 SECRET_KEY 사용
# 실제 프로덕션 환경에서는 환경 변수나 안전한 비밀 관리 서비스를 통해 관리해야 함
SECRET_KEY = os.getenv("SECRET_KEY", "d8e8fca2dc0f896fd7cb4cb0031ba249b6724b12f5acd1c8cff3b2a775f8c8f8")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "4320"))  # 3일로 연장
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # 30일

# --- 비밀번호 해싱 설정 ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- OAuth2 설정 ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    입력된 비밀번호와 해시된 비밀번호를 비교합니다.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """
    비밀번호를 해시화합니다.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    JWT 액세스 토큰을 생성합니다.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """
    JWT 리프레시 토큰을 생성합니다.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    """
    토큰을 디코딩하고 유효성을 검증합니다.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"JWT 에러: {str(e)}")
        return None

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> UserModel:
    """
    현재 인증된 사용자를 반환합니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info(f"토큰 검증 시작: {token[:10]}...")
        
        # 토큰 형식 검증
        if not token or not isinstance(token, str) or not token.strip():
            logger.error("토큰이 비어있거나 문자열이 아닙니다.")
            raise credentials_exception
            
        if not token.count('.') == 2:
            logger.error(f"잘못된 토큰 형식: 점(.) 개수가 2개가 아님 - {token[:10]}...")
            raise credentials_exception
        
        # 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"토큰 디코딩 성공: {payload}")
        
        username: str = payload.get("sub")
        if username is None:
            logger.error("토큰에 sub 클레임이 없음")
            raise credentials_exception
            
        logger.info(f"사용자 이름 추출: {username}")
    except JWTError as e:
        logger.error(f"JWT 에러: {str(e)}")
        raise credentials_exception
    
    # 사용자 조회
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user is None:
        logger.error(f"사용자를 찾을 수 없음: {username}")
        raise credentials_exception
        
    logger.info(f"사용자 인증 성공: {username}")
    return user

async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)]
) -> UserModel:
    """
    현재 활성화된 사용자를 반환합니다.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user