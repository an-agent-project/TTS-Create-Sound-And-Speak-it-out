import random
import time
from typing import Optional

from sqlalchemy.orm import Session

from app.models import User
from app.schemas import RegisterRequest


# 内存验证码存储（生产环境应使用 Redis）
_verification_codes: dict[str, tuple[str, float]] = {}

CODE_EXPIRE_SECONDS = 300  # 5 分钟有效期
CODE_LENGTH = 6


def generate_code(email: str) -> str:
    """生成6位数字验证码并存入内存"""
    code = "".join(str(random.randint(0, 9)) for _ in range(CODE_LENGTH))
    _verification_codes[email] = (code, time.time() + CODE_EXPIRE_SECONDS)
    return code


def verify_code(email: str, code: str) -> bool:
    """验证邮箱验证码是否正确且未过期"""
    entry = _verification_codes.get(email)
    if not entry:
        return False
    stored_code, expires_at = entry
    if time.time() > expires_at:
        del _verification_codes[email]
        return False
    if stored_code != code:
        return False
    # 验证成功后删除，防止重复使用
    del _verification_codes[email]
    return True


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, payload: RegisterRequest) -> User:
    password_hash, _ = User.hash_password(payload.password)
    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=password_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        return None
    if not User.verify_password(password, user.password_hash):
        return None
    return user
