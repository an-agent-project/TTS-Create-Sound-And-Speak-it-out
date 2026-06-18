from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import auth as auth_crud
from app.database import get_db
from app.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    SendCodeRequest,
    SendCodeResponse,
    UserRead,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/send-code", response_model=SendCodeResponse)
def send_verification_code(payload: SendCodeRequest) -> SendCodeResponse:
    """发送邮箱验证码"""
    code = auth_crud.generate_code(payload.email)
    # TODO: 生产环境接入真实邮件服务（如 SMTP / SendGrid）
    return SendCodeResponse(code=code)


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """验证码注册"""
    if not auth_crud.verify_code(payload.email, payload.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期",
        )
    if auth_crud.get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册",
        )
    user = auth_crud.create_user(db, payload)
    return AuthResponse(
        success=True,
        message="注册成功",
        user=UserRead(
            id=user.id,
            email=user.email,
            username=user.username,
            isActive=user.is_active,
            createdAt=user.created_at.isoformat() if user.created_at else "",
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """邮箱+密码登录"""
    user = auth_crud.authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
        )
    return AuthResponse(
        success=True,
        message="登录成功",
        user=UserRead(
            id=user.id,
            email=user.email,
            username=user.username,
            isActive=user.is_active,
            createdAt=user.created_at.isoformat() if user.created_at else "",
        ),
    )
