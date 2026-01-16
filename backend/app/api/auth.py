"""
用户认证 API
支持用户名密码注册和登录
"""
import hashlib
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_async_session
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger("house_advisor.api.auth")

router = APIRouter(prefix="/auth", tags=["用户认证"])


def hash_password(password: str) -> str:
    """密码哈希（简化版，使用 SHA256）"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return hash_password(password) == password_hash


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., description="用户名", min_length=3, max_length=20)
    password: str = Field(..., description="密码", min_length=6, max_length=50)
    nickname: Optional[str] = Field(None, description="昵称", max_length=50)


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class LoginByIdRequest(BaseModel):
    """通过 ID 登录请求（兼容旧版）"""
    user_id: str = Field(..., description="用户ID")


@router.post("/register", summary="用户注册")
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    注册新用户
    
    需要用户名和密码，昵称可选
    """
    logger.info(f"用户注册: username={request.username}")
    
    # 检查用户名是否已存在
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail={
                "code": 4002,
                "message": "用户名已存在"
            }
        )
    
    # 创建用户
    user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        nickname=request.nickname or request.username
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"用户注册成功: id={user.id}, username={user.username}")
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "user_id": str(user.id),
            "username": user.username,
            "nickname": user.nickname,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }


@router.post("/login", summary="用户登录")
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    用户登录
    
    使用用户名和密码登录
    """
    logger.info(f"用户登录: username={request.username}")
    
    # 查询用户
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "code": 4001,
                "message": "用户名或密码错误"
            }
        )
    
    # 验证密码
    if not user.password_hash or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={
                "code": 4001,
                "message": "用户名或密码错误"
            }
        )
    
    logger.info(f"用户登录成功: id={user.id}, username={user.username}")
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "user_id": str(user.id),
            "username": user.username,
            "nickname": user.nickname,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }


@router.post("/login-by-id", summary="通过ID登录（兼容旧版）")
async def login_by_id(
    request: LoginByIdRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    通过 user_id 登录（兼容旧版客户端）
    """
    logger.info(f"用户通过ID登录: user_id={request.user_id}")
    
    # 查询用户
    result = await db.execute(
        select(User).where(User.id == request.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "code": 4001,
                "message": "用户不存在"
            }
        )
    
    logger.info(f"用户登录成功: id={user.id}")
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "user_id": str(user.id),
            "username": user.username,
            "nickname": user.nickname,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }


@router.get("/me", summary="获取当前用户信息")
async def get_current_user(
    user_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    获取用户信息
    """
    # 查询用户
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail={
                "code": 4001,
                "message": "用户不存在"
            }
        )
    
    return {
        "code": 0,
        "message": "success",
        "data": {
            "user_id": str(user.id),
            "username": user.username,
            "nickname": user.nickname,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }
