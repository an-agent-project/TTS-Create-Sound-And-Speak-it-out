"""Small startup migrations for existing local databases.

SQLAlchemy's create_all() creates missing tables, but it does not alter tables
that already exist. Keep these migrations narrow and idempotent so older local
MySQL databases can run the current ORM models.
"""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_runtime_schema(engine: Engine) -> None:
    """Apply idempotent schema fixes required by the current ORM models."""
    inspector = inspect(engine)
    if "voices" in inspector.get_table_names():
        _ensure_voices_source_voice_id(engine, inspector)


def _ensure_voices_source_voice_id(engine: Engine, inspector) -> None:
    column_names = {column["name"] for column in inspector.get_columns("voices")}
    if "source_voice_id" in column_names:
        return

    if engine.dialect.name == "mysql":
        statements = [
            "ALTER TABLE voices ADD COLUMN source_voice_id BIGINT UNSIGNED NULL AFTER owner_id",
            "ALTER TABLE voices ADD INDEX idx_voice_source_voice (source_voice_id)",
        ]
    else:
        statements = ["ALTER TABLE voices ADD COLUMN source_voice_id INTEGER NULL"]

    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))