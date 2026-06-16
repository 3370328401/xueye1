from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.schemas import LoginIn, RegisterIn, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=TokenOut)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.phone == data.phone).first():
        raise HTTPException(status_code=400, detail="该手机号已注册")
    user = User(
        name=data.name,
        phone=data.phone,
        password=hash_password(data.password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.id)
    return TokenOut(
        access_token=token, role=user.role, name=user.name, user_id=user.id
    )


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="手机号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")
    token = create_access_token(user.id)
    return TokenOut(
        access_token=token, role=user.role, name=user.name, user_id=user.id
    )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    # 简单 Token 认证，前端清除本地 Token 即可
    return {"message": "已退出登录"}
