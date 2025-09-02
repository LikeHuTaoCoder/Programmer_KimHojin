from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 데이터베이스 연결 설정
DATABASE_URL = "mysql://root:0414@localhost:3308/pb_book_db"

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, echo=False)

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 베이스 모델
Base = declarative_base()

# 데이터베이스 세션 생성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
