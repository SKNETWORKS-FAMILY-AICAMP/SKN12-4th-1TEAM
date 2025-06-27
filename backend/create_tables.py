from app.models.db import Base, engine
from app.models.user import User, ChatMessage
from app.models.chat import Session, ChatLog

def create_tables():
    """
    데이터베이스 테이블을 생성합니다.
    이미 존재하는 테이블은 건너뜁니다.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables() 