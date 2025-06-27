from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import logging
import os
import requests
from urllib.parse import urlencode
import json
import secrets
import uuid
import httpx
import jwt 
from datetime import datetime, timedelta, timezone 

from app.core.security import (
    get_current_active_user,
    get_password_hash,
    create_access_token,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_refresh_token,
    decode_token
)

from app.models.db import get_db
from app.models.user import User as UserModel, ChatMessage as ChatMessageModel
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    Token,
    ChatMessageCreate,
    ChatMessage
)
from datetime import timedelta

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# 환경 변수에서 OAuth 설정 가져오기
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")

# 우리 서비스의 JWT 설정
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# 네이버 로그인 설정 
@router.get('/v1/login/naver')
async def get_naver_login_url():
    """
    네이버 로그인 URL을 반환합니다.
    """
    state = str(uuid.uuid4())
    naver_auth_url = (
        f"https://nid.naver.com/oauth2.0/authorize?"
        f"response_type=code&"
        f"client_id={NAVER_CLIENT_ID}&"
        f"redirect_uri={NAVER_REDIRECT_URI}&"
        f"state={state}"
    )
    return {"naver_auth_url": naver_auth_url}

# 네이버 로그인 콜백 처리
@router.get('/v1/login/naver/callback')
async def naver_callback(request: Request, code: str, state: str, db: Session = Depends(get_db)):
    """
    네이버 로그인 콜백 처리
    """
    try:
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not found.")
        # 1. Access Token 요청 
        token_url = "https://nid.naver.com/oauth2.0/token"
        token_params = {
            "grant_type": "authorization_code",
            "client_id": NAVER_CLIENT_ID,
            "client_secret": NAVER_CLIENT_SECRET,
            "code": code,
            "state": state
        }
        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, params=token_params)
            token_data = token_response.json()
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data["error_description"])
        
        # 2. 사용자 정보 요청
        user_info_url = "https://openapi.naver.com/v1/nid/me"
        headers = {
            "Authorization": f"Bearer {token_data['access_token']}"
        }
        
        async with httpx.AsyncClient() as client:
            profile_response = await client.get(user_info_url, headers=headers)
            profile_data = profile_response.json()

        if profile_data.get("resultcode") != "00":
            raise HTTPException(status_code=500, detail="Failed to get user profile from Naver.")
        
        user_info = profile_data.get("response")
        email = user_info.get("email")
        name = user_info.get("name")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Naver.")

        # 3. 사용자 정보 처리(DB에서 사용자 확인 및 또는 생성 처리)
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            # 중복 방지를 위한 사용자명 생성
            base_username = email.split("@")[0]
            username = base_username
            counter = 1
            
            # 중복 확인 및 고유한 username 생성
            while get_user_by_username(db, username):
                username = f"{base_username}{counter}"
                counter += 1
                
            # 중복 방지를 위한 닉네임 생성
            base_nickname = name or base_username
            nickname = base_nickname
            counter = 1
            
            # 중복 확인 및 고유한 nickname 생성
            while get_user_by_nickname(db, nickname):
                nickname = f"{base_nickname}{counter}"
                counter += 1
                
            user = UserModel(
                email=email,
                username=username,
                nickname=nickname,
                hashed_password=get_password_hash(secrets.token_hex(16)),  # 임의 비밀번호
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 4. JWT 토큰 생성 - create_access_token 함수 사용
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # 리프레시 토큰 생성
        refresh_token = create_refresh_token(
            data={"sub": user.username}
        )
        
        # 5. 토큰을 쿼리 파라미터로 포함하여 React 앱으로 리디렉션
        redirect_url = f"{FRONTEND_URL}/login/success?token={access_token}&refresh_token={refresh_token}"
        return RedirectResponse(redirect_url)
    except Exception as e:
        logger.error(f"Error in Naver callback: {str(e)}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=server_error"
        )

# 구글 소셜 로그인 (Google OAuth 2.0 사용)
@router.get('/v1/login/google')
async def get_google_login_url():
    """
    React 앱에서 '구글로 로그인' 버튼 클릭시 호출 될 API.
    구글 로그인 페이지로 리디렉션 할 URL을 생성하여 반환 
    """
    state = str(uuid.uuid4())
    scope = "openid email profile"
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope={scope}&"
        f"state={state}"
    )
    return {"google_auth_url": google_auth_url}

@router.get("/login/google/callback")
async def google_login_callback(request: Request, code: str = None, state: str = None, db: Session = Depends(get_db)):
    """
    구글로부터 인증 코드를 받아 액세스 토큰 및 사용자 정보를 요청하고,
    자체 JWT를 발급하여 React 앱으로 리디렉션합니다.
    """
    try:
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not found.")

        # 1. 구글로부터 Access Token 및 ID Token 요청
        token_url = "https://oauth2.googleapis.com/token"
        token_params = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI,
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=token_params)
            token_data = token_response.json()
        
        if "error" in token_data:
            error_desc = token_data.get('error_description', token_data.get('error', 'Unknown error'))
            raise HTTPException(status_code=400, detail=f"Google Error: {error_desc}")

        id_token = token_data.get("id_token")
        if not id_token:
            raise HTTPException(status_code=500, detail="id_token not found in response from Google.")

        # 2. ID Token을 디코딩하여 사용자 정보 추출
        try:
            # 서명 검증 없이 디코딩. 실제 프로덕션에서는 구글 공개키로 서명을 검증해야 더 안전합니다.
            decoded_payload = jwt.decode(id_token, options={"verify_signature": False})
            email = decoded_payload.get("email")
            name = decoded_payload.get("name")
            
            if not email:
                raise HTTPException(status_code=400, detail="Email not provided by Google.")
                
            logger.info(f"로그인 성공 (Google): {name} ({email})")
        except Exception as e:
            logger.error(f"Error decoding Google id_token: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to decode id_token: {str(e)}")

        # 3. 사용자 정보 처리(DB에서 사용자 확인 및 또는 생성 처리)
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            # 중복 방지를 위한 사용자명 생성
            base_username = email.split("@")[0]
            username = base_username
            counter = 1
            
            # 중복 확인 및 고유한 username 생성
            while get_user_by_username(db, username):
                username = f"{base_username}{counter}"
                counter += 1
                
            # 중복 방지를 위한 닉네임 생성
            base_nickname = name or base_username
            nickname = base_nickname
            counter = 1
            
            # 중복 확인 및 고유한 nickname 생성
            while get_user_by_nickname(db, nickname):
                nickname = f"{base_nickname}{counter}"
                counter += 1
                
            user = UserModel(
                email=email,
                username=username,
                nickname=nickname,
                hashed_password=get_password_hash(secrets.token_hex(16)),  # 임의 비밀번호
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # 4. JWT 토큰 생성 - create_access_token 함수 사용
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        # 리프레시 토큰 생성
        refresh_token = create_refresh_token(
            data={"sub": user.username}
        )
        
        # 5. React 앱의 메인 페이지로 토큰과 함께 리디렉션
        redirect_url = f"{FRONTEND_URL}?token={access_token}&refresh_token={refresh_token}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Error in Google callback: {str(e)}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=server_error&message={str(e)}"
        )

def get_user_by_username(db: Session, username: str):
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_user_by_nickname(db: Session, nickname: str):
    return db.query(UserModel).filter(UserModel.nickname == nickname).first()

@router.post("/signup", response_model=UserSchema, summary="회원가입")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    새로운 사용자를 생성합니다.
    - **user**: 사용자 생성에 필요한 정보 (이메일, 아이디, 닉네임, 비밀번호)
    """
    # 요청 데이터 로깅
    logger.info(f"회원가입 요청: {user.dict(exclude={'password'})}")
    
    try:
        # 이메일 중복 확인
        db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
        if db_user:
            logger.warning(f"이메일 중복: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # 아이디 중복 확인
        db_user = get_user_by_username(db, username=user.username)
        if db_user:
            logger.warning(f"아이디 중복: {user.username}")
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # 닉네임 중복 확인
        db_user = get_user_by_nickname(db, nickname=user.nickname)
        if db_user:
            logger.warning(f"닉네임 중복: {user.nickname}")
            raise HTTPException(status_code=400, detail="Nickname already registered")
        
        # 비밀번호 해싱
        hashed_password = get_password_hash(user.password)
        
        # 새 사용자 생성
        db_user = UserModel(
            email=user.email,
            username=user.username,
            nickname=user.nickname,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"회원가입 성공: {user.username}")
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"회원가입 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/login", response_model=Token, summary="로그인")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Login attempt for username: {form_data.username}")
        logger.debug(f"Received password length: {len(form_data.password)}")
        
        user = get_user_by_username(db, username=form_data.username)
        if not user:
            logger.warning(f"User not found: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"Found user: {user.username}, stored password hash length: {len(user.hashed_password)}")
        
        # 비밀번호 검증 로깅 추가
        try:
            is_valid = verify_password(form_data.password, user.hashed_password)
            logger.info(f"Password verification result for {form_data.username}: {is_valid}")
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error verifying password",
            )
        
        if not is_valid:
            logger.warning(f"Invalid password for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 액세스 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # 리프레시 토큰 생성
        refresh_token = create_refresh_token(
            data={"sub": user.username}
        )
        
        logger.info(f"Login successful for user: {form_data.username}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "username": user.username,
                "nickname": user.nickname,
                "email": user.email,
            },
        }
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}",
        )

@router.get("/me", response_model=UserSchema, summary="내 정보 확인 (인증 필요)")
async def read_users_me(
    current_user: Annotated[UserSchema, Depends(get_current_active_user)]
):
    return current_user

@router.get("/check-username", summary="아이디 중복 확인")
def check_username(username: str, db: Session = Depends(get_db)):
    """
    입력된 username(아이디)이 사용 가능한지 확인합니다.
    - **username**: 확인할 사용자 아이디
    - **returns**: 사용 가능 여부 (available: true/false)
    """
    user = get_user_by_username(db, username=username)
    if user:
        return {"available": False}
    return {"available": True}

@router.get("/check-nickname", summary="닉네임 중복 확인")
def check_nickname(nickname: str, db: Session = Depends(get_db)):
    """
    입력된 nickname(닉네임)이 사용 가능한지 확인합니다.
    - **nickname**: 확인할 닉네임
    - **returns**: 사용 가능 여부 (available: true/false)
    """
    user = get_user_by_nickname(db, nickname=nickname)
    if user:
        return {"available": False}
    return {"available": True}

@router.post("/messages", response_model=ChatMessage, summary="대화 메시지 전송 (인증 필요)")
def create_chat_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    현재 로그인된 사용자의 새 대화 메시지를 데이터베이스에 저장합니다.
    """
    db_message = ChatMessageModel(**message.dict(), owner=current_user)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/messages", response_model=List[ChatMessage], summary="대화 기록 조회 (인증 필요)")
def read_chat_messages(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    현재 로그인된 사용자의 모든 대화 기록을 반환합니다.
    """
    return current_user.messages

@router.post("/logout", summary="로그아웃")
async def logout(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
    db: Session = Depends(get_db)
):
    """
    사용자 로그아웃을 처리합니다.
    """
    logger.info(f"Logout request for user: {current_user.username}")
    return {"message": "Successfully logged out"}

# 중복된 구글 로그인 엔드포인트 제거 (v1/login/google 사용)

@router.get("/login/naver")
async def naver_login():
    """네이버 로그인 시작점"""
    client_id = os.getenv("NAVER_CLIENT_ID")
    redirect_uri = os.getenv("NAVER_REDIRECT_URI")
    state = secrets.token_hex(16)  # CSRF 방지를 위한 상태 토큰
    
    # 네이버 로그인 페이지 URL 생성
    auth_url = "https://nid.naver.com/oauth2.0/authorize"
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state
    }
    
    return RedirectResponse(
        url=f"{auth_url}?{urlencode(params)}",
        status_code=status.HTTP_302_FOUND
    )

@router.get("/login/naver/callback")
async def naver_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    try:
        # 네이버 토큰 얻기
        token_url = "https://nid.naver.com/oauth2.0/token"
        token_params = {
            "grant_type": "authorization_code",
            "client_id": os.getenv("NAVER_CLIENT_ID"),
            "client_secret": os.getenv("NAVER_CLIENT_SECRET"),
            "code": code,
            "state": state
        }
        token_response = requests.get(token_url, params=token_params)
        token_data = token_response.json()

        if "error" in token_data:
            logger.error(f"Naver token error: {token_data}")
            return RedirectResponse(
                url=f"{os.getenv('FRONTEND_URL')}/login?error=token_error",
                status_code=status.HTTP_302_FOUND
            )

        access_token = token_data.get("access_token")
        
        # 네이버 사용자 정보 얻기
        user_info_response = requests.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = user_info_response.json()

        if user_info.get("resultcode") != "00":
            logger.error(f"Naver API error: {user_info}")
            return RedirectResponse(
                url=f"{os.getenv('FRONTEND_URL')}/login?error=api_error",
                status_code=status.HTTP_302_FOUND
            )

        naver_account = user_info.get("response", {})
        email = naver_account.get("email")
        name = naver_account.get("name")
        
        if not email:
            logger.error("No email from Naver")
            return RedirectResponse(
                url=f"{os.getenv('FRONTEND_URL')}/login?error=no_email",
                status_code=status.HTTP_302_FOUND
            )

        # DB에서 사용자 찾기 또는 생성
        user = db.query(UserModel).filter(UserModel.email == email).first()
        if not user:
            # 중복 방지를 위한 사용자명 생성
            base_username = email.split("@")[0]
            username = base_username
            counter = 1
            
            # 중복 확인 및 고유한 username 생성
            while get_user_by_username(db, username):
                username = f"{base_username}{counter}"
                counter += 1
                
            # 중복 방지를 위한 닉네임 생성
            base_nickname = name or base_username
            nickname = base_nickname
            counter = 1
            
            # 중복 확인 및 고유한 nickname 생성
            while get_user_by_nickname(db, nickname):
                nickname = f"{base_nickname}{counter}"
                counter += 1
                
            user = UserModel(
                email=email,
                username=username,
                nickname=nickname,
                hashed_password=get_password_hash(secrets.token_hex(16)),  # 임의 비밀번호
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # JWT 토큰 생성 - username을 sub에 사용
        jwt_token = create_access_token(
            data={"sub": user.username},  # email 대신 username 사용
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # 리프레시 토큰 생성
        refresh_token = create_refresh_token(
            data={"sub": user.username}
        )

        # 사용자 정보를 JSON으로 직렬화
        user_data = {
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email
        }

        # 프론트엔드로 리다이렉트 (메인 페이지로 토큰과 함께)
        redirect_url = f"{FRONTEND_URL}?token={jwt_token}&refresh_token={refresh_token}"
        return RedirectResponse(url=redirect_url)

    except Exception as e:
        logger.error(f"Error in Naver callback: {str(e)}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=server_error"
        )

@router.post("/refresh-token", response_model=Token, summary="토큰 갱신")
async def refresh_access_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    리프레시 토큰을 사용하여 액세스 토큰을 갱신합니다.
    """
    try:
        # 요청 본문에서 리프레시 토큰 추출
        try:
            body = await request.json()
            refresh_token = body.get("refresh_token")
            if not refresh_token:
                logger.error("리프레시 토큰이 제공되지 않았습니다.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="리프레시 토큰이 필요합니다.",
                )
        except Exception as e:
            logger.error(f"요청 본문 파싱 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효한 JSON 요청 본문이 필요합니다.",
            )
            
        # 리프레시 토큰 검증
        payload = decode_token(refresh_token)
        if not payload:
            logger.error("유효하지 않은 리프레시 토큰")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 리프레시 토큰",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        username = payload.get("sub")
        if not username:
            logger.error("토큰에 사용자 식별자가 없습니다.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰 형식",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # 사용자 조회
        user = db.query(UserModel).filter(UserModel.username == username).first()
        if not user:
            logger.error(f"사용자를 찾을 수 없음: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # 사용자 활성 상태 확인
        if not user.is_active:
            logger.error(f"사용자 {username}가 비활성 상태입니다.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="비활성 사용자",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 새 액세스 토큰 및 리프레시 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        
        new_refresh_token = create_refresh_token(
            data={"sub": username}
        )
        
        logger.info(f"토큰이 갱신되었습니다. 사용자: {username}")
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": {
                "username": user.username,
                "nickname": user.nickname,
                "email": user.email,
            },
        }
    except Exception as e:
        logger.error(f"토큰 갱신 오류: {str(e)}")
        # 오류 유형에 따라 적절한 상태 코드 반환
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"토큰 갱신 오류: {str(e)}",
        )

