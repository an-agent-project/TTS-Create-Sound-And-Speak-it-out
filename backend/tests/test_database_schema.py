from pathlib import Path

from app.database import DEFAULT_DATABASE_URL


ROOT_DIR = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT_DIR / "backend" / "db" / "init.sql"
DESIGN_DOC_PATH = ROOT_DIR / "数据库设计.md"


def test_database_schema_defines_voice_preview_cache_tables():
    sql = SCHEMA_PATH.read_text(encoding="utf-8").lower()

    for table_name in (
        "voices",
        "voice_provider_profiles",
        "voice_preview_audios",
    ):
        assert f"create table if not exists {table_name}" in sql

    assert "constraint fk_provider_voice" in sql
    assert "constraint fk_preview_provider_profile" in sql
    assert "unique key uk_provider_voice" in sql
    assert "unique key uk_preview_cache" in sql


def test_backend_defaults_to_mysql_database():
    assert DEFAULT_DATABASE_URL.startswith("mysql+pymysql://")


def test_database_schema_seeds_xiaoxiao_edge_tts_voice():
    sql = SCHEMA_PATH.read_text(encoding="utf-8")

    assert "zh-CN-XiaoxiaoNeural" in sql
    assert "晓晓" in sql
    assert "edge_tts" in sql


def test_database_design_document_exists_and_explains_storage_boundary():
    doc = DESIGN_DOC_PATH.read_text(encoding="utf-8")

    assert "voices" in doc
    assert "voice_provider_profiles" in doc
    assert "voice_preview_audios" in doc
    assert "MySQL 不直接保存音频二进制" in doc
    assert "Edge-TTS" in doc
    assert "Qwen-TTS" in doc
