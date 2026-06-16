from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base


def make_client():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_voice_crud_lifecycle():
    client = make_client()

    create_response = client.post(
        "/api/voices",
        json={
            "voiceKey": "xiaoxiao",
            "displayName": "晓晓",
            "gender": "female",
            "style": "温柔",
            "category": "知识类",
            "description": "温柔知性的女声，适合知识讲解、课程录制",
            "isRecommended": True,
            "providers": [
                {
                    "provider": "edge_tts",
                    "providerVoiceId": "zh-CN-XiaoxiaoNeural",
                    "locale": "zh-CN",
                    "supportsMp3": True,
                    "supportsWav": False,
                    "isDefault": True,
                }
            ],
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["voiceKey"] == "xiaoxiao"
    assert created["displayName"] == "晓晓"
    assert created["providers"][0]["providerVoiceId"] == "zh-CN-XiaoxiaoNeural"

    voice_id = created["id"]

    list_response = client.get("/api/voices?category=知识类&gender=female&recommendedOnly=true")
    assert list_response.status_code == 200
    assert [item["voiceKey"] for item in list_response.json()] == ["xiaoxiao"]

    detail_response = client.get(f"/api/voices/{voice_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["providers"][0]["provider"] == "edge_tts"

    update_response = client.put(
        f"/api/voices/{voice_id}",
        json={"style": "知性", "description": "更新后的描述"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["style"] == "知性"
    assert update_response.json()["description"] == "更新后的描述"

    delete_response = client.delete(f"/api/voices/{voice_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/voices/{voice_id}")
    assert missing_response.status_code == 404


def test_create_voice_rejects_duplicate_voice_key():
    client = make_client()
    payload = {
        "voiceKey": "yunxi",
        "displayName": "云希",
        "gender": "male",
        "style": "磁性",
        "category": "故事类",
        "description": "磁性的男声，适合故事叙述、播客节目",
    }

    assert client.post("/api/voices", json=payload).status_code == 201
    duplicate_response = client.post("/api/voices", json=payload)

    assert duplicate_response.status_code == 400
    assert "voiceKey already exists" in duplicate_response.text
