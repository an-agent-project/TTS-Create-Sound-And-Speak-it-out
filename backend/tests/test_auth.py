from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base


def make_client():
    """Return a TestClient wired to an in-memory SQLite database."""
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


# ── Registration ──────────────────────────────────────────────


def test_register_creates_user_and_returns_token():
    client = make_client()
    resp = client.post(
        "/api/auth/register",
        json={"username": "alice", "password": "secret1234"},
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == "alice"
    assert body["user"]["email"] is None


def test_register_duplicate_username_is_rejected():
    client = make_client()
    payload = {"username": "bob", "password": "pass1234"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409
    assert "already taken" in resp.json()["detail"]


def test_register_rejects_short_password():
    client = make_client()
    resp = client.post(
        "/api/auth/register",
        json={"username": "eve", "password": "ab"},
    )
    assert resp.status_code == 422


# ── Login ─────────────────────────────────────────────────────


def test_login_returns_token_for_valid_credentials():
    client = make_client()
    client.post(
        "/api/auth/register",
        json={"username": "charlie", "password": "mypassword"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"username": "charlie", "password": "mypassword"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["user"]["username"] == "charlie"


def test_login_rejects_wrong_password():
    client = make_client()
    client.post(
        "/api/auth/register",
        json={"username": "dave", "password": "correct"},
    )
    resp = client.post(
        "/api/auth/login",
        json={"username": "dave", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert "invalid username or password" in resp.json()["detail"]


def test_login_rejects_nonexistent_user():
    client = make_client()
    resp = client.post(
        "/api/auth/login",
        json={"username": "ghost", "password": "nope"},
    )
    assert resp.status_code == 401


# ── GET /me ───────────────────────────────────────────────────


def test_get_me_returns_authenticated_user():
    client = make_client()
    reg = client.post(
        "/api/auth/register",
        json={"username": "frank", "password": "secret5678"},
    )
    token = reg.json()["access_token"]
    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "frank"


def test_get_me_rejects_missing_token():
    client = make_client()
    resp = client.get("/api/auth/me")
    assert resp.status_code == 422  # FastAPI requires the Header


def test_get_me_rejects_invalid_token():
    client = make_client()
    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert resp.status_code == 401


def test_get_me_rejects_wrong_scheme():
    client = make_client()
    reg = client.post(
        "/api/auth/register",
        json={"username": "grace", "password": "secret000"},
    )
    token = reg.json()["access_token"]
    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Basic {token}"},
    )
    assert resp.status_code == 401
    assert "Bearer" in resp.json()["detail"]


# ── PUT /me ───────────────────────────────────────────────────


def test_update_me_changes_profile_fields():
    client = make_client()
    reg = client.post(
        "/api/auth/register",
        json={"username": "heidi", "password": "pw123456"},
    )
    token = reg.json()["access_token"]

    resp = client.put(
        "/api/auth/me",
        json={"phone": "13800138000", "email": "heidi@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["phone"] == "13800138000"
    assert body["email"] == "heidi@example.com"

    # Confirm persistence via GET /me
    me = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.json()["phone"] == "13800138000"
    assert me.json()["email"] == "heidi@example.com"
