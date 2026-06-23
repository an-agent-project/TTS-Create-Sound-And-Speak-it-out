from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
LOGIN_PAGE_PATH = ROOT_DIR / "src" / "views" / "LoginPage.vue"
AUTH_MODAL_PATH = ROOT_DIR / "src" / "components" / "UserAuthModal.vue"


def test_auth_views_show_development_verification_code_from_api_response():
    for path in (LOGIN_PAGE_PATH, AUTH_MODAL_PATH):
        source = path.read_text(encoding="utf-8")

        assert "data.code" in source
        assert "开发验证码" in source
