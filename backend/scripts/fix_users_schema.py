import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import inspect, text
from app.database import engine

statements = []
with engine.connect() as conn:
    inspector = inspect(conn)
    columns = {column["name"]: column for column in inspector.get_columns("users")}
    indexes = {index["name"] for index in inspector.get_indexes("users")}

if columns.get("email", {}).get("type") is not None:
    statements.append("ALTER TABLE users MODIFY email VARCHAR(255) NULL")
if "role" not in columns:
    statements.append("ALTER TABLE users ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'user' AFTER is_active")
if "avatar" in columns:
    statements.append("ALTER TABLE users MODIFY avatar MEDIUMTEXT NULL")
if "is_active" in columns:
    statements.append("ALTER TABLE users MODIFY is_active BOOLEAN NOT NULL DEFAULT TRUE")
if "uk_user_email" not in indexes:
    statements.append("ALTER TABLE users ADD UNIQUE KEY uk_user_email (email)")

with engine.begin() as conn:
    for statement in statements:
        print(statement)
        conn.execute(text(statement))

print("users schema migration ok")
