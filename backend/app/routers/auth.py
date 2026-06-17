from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.audit import record_audit
from app.core.constants import ROLE_DONOR
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas import (
    CodeLoginIn,
    LoginIn,
    RegisterIn,
    TokenOut,
    UserOut,
    WechatLoginIn,
)

router = APIRouter(prefix="/auth", tags=["认证"])

# MVP 阶段不接真实短信网关，固定模拟验证码
MOCK_SMS_CODE = "123456"


def _token(user: User) -> TokenOut:
    return TokenOut(
        access_token=create_access_token(user.id),
        role=user.role,
        name=user.name,
        user_id=user.id,
    )


@router.post("/register", response_model=TokenOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(status_code=400, detail="该手机号已注册")
    user = User(
        name=data.name,
        phone=data.phone,
        password=hash_password(data.password),
        role=ROLE_DONOR,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    record_audit(db, user, "注册", user.phone)
    return _token(user)


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="手机号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    record_audit(db, user, "登录", "密码登录")
    return _token(user)


@router.post("/login-code", response_model=TokenOut)
def login_code(data: CodeLoginIn, db: Session = Depends(get_db)):
    """手机验证码登录（模拟）。验证码固定为 123456；新手机号自动注册为个人献血者。"""
    if data.code != MOCK_SMS_CODE:
        raise HTTPException(status_code=400, detail=f"验证码错误（模拟验证码为 {MOCK_SMS_CODE}）")
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user:
        user = User(
            name=f"献血者{data.phone[-4:]}",
            phone=data.phone,
            password=hash_password(MOCK_SMS_CODE),
            role=ROLE_DONOR,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    record_audit(db, user, "登录", "验证码登录")
    return _token(user)


@router.post("/login-wechat", response_model=TokenOut)
def login_wechat(data: WechatLoginIn, db: Session = Depends(get_db)):
    """微信授权登录（模拟）。根据 openid 查找/创建用户。"""
    openid = data.openid or "MOCK-OPENID-0001"
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        phone = f"wx{openid[-8:]}"
        user = User(
            name="微信用户",
            phone=phone,
            password=hash_password("wechat"),
            role=ROLE_DONOR,
            openid=openid,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    record_audit(db, user, "登录", "微信登录")
    return _token(user)


@router.get("/send-code")
def send_code(phone: str):
    """发送短信验证码（模拟）。"""
    return {"message": "验证码已发送（模拟）", "code": MOCK_SMS_CODE}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    # 简单 Token 认证，前端清除本地 Token 即可
    return {"message": "已退出登录"}
