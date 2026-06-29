import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.env import load_env

load_env()

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


def ensure_legacy_schema() -> None:
    with engine.begin() as conn:
        voice_columns = {column["name"] for column in inspect(engine).get_columns("voices")}
        if "source_voice_id" not in voice_columns:
            if engine.dialect.name == "mysql":
                conn.execute(text("ALTER TABLE voices ADD COLUMN source_voice_id INT NULL"))
                conn.execute(text("CREATE INDEX ix_voices_source_voice_id ON voices (source_voice_id)"))
            else:
                conn.execute(text("ALTER TABLE voices ADD COLUMN source_voice_id INTEGER NULL"))

        material_columns = {column["name"] for column in inspect(engine).get_columns("materials")}
        if "owner_id" not in material_columns:
            if engine.dialect.name == "mysql":
                conn.execute(text("ALTER TABLE materials ADD COLUMN owner_id INT NULL"))
                conn.execute(text("CREATE INDEX ix_materials_owner_id ON materials (owner_id)"))
            else:
                conn.execute(text("ALTER TABLE materials ADD COLUMN owner_id INTEGER NULL"))
