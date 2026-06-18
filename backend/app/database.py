import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DEFAULT_DATABASE_URL = "mysql+pymysql://root:123456@127.0.0.1:3306/tts_podcast?charset=utf8mb4"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
