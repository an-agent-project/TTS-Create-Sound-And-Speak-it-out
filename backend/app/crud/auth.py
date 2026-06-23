import random
import time
from typing import Optional

from sqlalchemy.orm import Session

from app.auth import hash_password, verify_password
from app.models import User
from app.schemas import RegisterRequest


# In-memory verification-code store. Use Redis or another shared store in production.
_verification_codes: dict[str, tuple[str, float]] = {}

CODE_EXPIRE_SECONDS = 300
CODE_LENGTH = 6


def generate_code(email: str) -> str:
    code = "".join(str(random.randint(0, 9)) for _ in range(CODE_LENGTH))
    _verification_codes[email] = (code, time.time() + CODE_EXPIRE_SECONDS)
    return code


def verify_code(email: str, code: str) -> bool:
    entry = _verification_codes.get(email)
    if not entry:
        return False
    stored_code, expires_at = entry
    if time.time() > expires_at:
        del _verification_codes[email]
        return False
    if stored_code != code:
        return False
    del _verification_codes[email]
    return True


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, payload: RegisterRequest) -> User:
    user = User(
        email=payload.email,
        username=payload.username,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
