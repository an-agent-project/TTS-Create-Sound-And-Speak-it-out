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
    table_names = inspector.get_table_names()
    if "voices" in table_names:
        _ensure_voices_source_voice_id(engine, inspector)
    if "voice_publish_requests" not in table_names:
        _create_voice_publish_requests(engine)


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

def _create_voice_publish_requests(engine: Engine) -> None:
    if engine.dialect.name == "mysql":
        statement = """
        CREATE TABLE IF NOT EXISTS voice_publish_requests (
          id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
          source_voice_id BIGINT UNSIGNED NOT NULL,
          requester_id BIGINT UNSIGNED NOT NULL,
          public_voice_id BIGINT UNSIGNED NULL,
          status VARCHAR(20) NOT NULL DEFAULT 'pending',
          request_note VARCHAR(500) NULL,
          review_note VARCHAR(500) NULL,
          reviewed_by BIGINT UNSIGNED NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          PRIMARY KEY (id),
          KEY idx_voice_publish_status (status),
          KEY idx_voice_publish_source (source_voice_id),
          KEY idx_voice_publish_requester (requester_id),
          KEY idx_voice_publish_public_voice (public_voice_id),
          CONSTRAINT fk_voice_publish_source
            FOREIGN KEY (source_voice_id) REFERENCES voices(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
          CONSTRAINT fk_voice_publish_requester
            FOREIGN KEY (requester_id) REFERENCES users(id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,
          CONSTRAINT fk_voice_publish_public_voice
            FOREIGN KEY (public_voice_id) REFERENCES voices(id)
            ON DELETE SET NULL
            ON UPDATE CASCADE,
          CONSTRAINT fk_voice_publish_reviewer
            FOREIGN KEY (reviewed_by) REFERENCES users(id)
            ON DELETE SET NULL
            ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
    else:
        statement = """
        CREATE TABLE IF NOT EXISTS voice_publish_requests (
          id INTEGER NOT NULL PRIMARY KEY,
          source_voice_id INTEGER NOT NULL,
          requester_id INTEGER NOT NULL,
          public_voice_id INTEGER NULL,
          status VARCHAR(20) NOT NULL DEFAULT 'pending',
          request_note VARCHAR(500) NULL,
          review_note VARCHAR(500) NULL,
          reviewed_by INTEGER NULL,
          created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """

    with engine.begin() as conn:
        conn.execute(text(statement))