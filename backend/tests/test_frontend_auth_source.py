from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
LOGIN_PAGE_PATH = ROOT_DIR / "src" / "views" / "LoginPage.vue"
AUTH_MODAL_PATH = ROOT_DIR / "src" / "components" / "UserAuthModal.vue"


def test_auth_views_show_development_verification_code_from_api_response():
    for path in (LOGIN_PAGE_PATH, AUTH_MODAL_PATH):
        source = path.read_text(encoding="utf-8")

        assert "data.code" in source
        assert "开发验证码" in source


def test_login_page_supports_password_reset_flow():
    login_page = LOGIN_PAGE_PATH.read_text(encoding="utf-8")
    api_source = (ROOT_DIR / "src" / "services" / "api.js").read_text(encoding="utf-8")

    assert "forgotPassword" in login_page
    assert "isResetPassword" in login_page
    assert "resetForm" in login_page
    assert "handleResetPassword" in login_page
    assert "sendAuthCode(email)" in login_page
    assert "resetPassword({ email, code, newPassword: resetForm.newPassword })" in login_page
    assert 'request("/auth/send-code"' in api_source
    assert 'request("/auth/reset-password"' in api_source


def test_profile_avatar_is_compressed_and_persisted_before_preview_update():
    profile_source = (ROOT_DIR / "src" / "views" / "ProfilePage.vue").read_text(encoding="utf-8")
    store_source = (ROOT_DIR / "src" / "stores" / "app.js").read_text(encoding="utf-8")

    assert "compressAvatarFile" in profile_source
    assert "await store.updateMe({ avatar })" in profile_source
    assert "reader.result" not in profile_source
    assert "previousUser" in store_source
    assert "throw new Error" in store_source
    assert "setUser(await resp.json())" in store_source
