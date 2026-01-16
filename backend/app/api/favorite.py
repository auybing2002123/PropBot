"""
收藏 API
处理用户收藏的问答对
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_async_session
from app.models.favorite import Favorite
from app.utils.logger import get_logger

logger = get_logger("house_advisor.api.favorite")

router = APIRouter(prefix="/favorites", tags=["收藏"])


class FavoriteCreate(BaseModel):
    """创建收藏请求"""
    user_id: str = Field(..., description="用户ID")
    message_id: Optional[str] = Field(default=None, description="关联消息ID")
    conversation_id: Optional[str] = Field(default=None, description="关联对话ID")
    question: str = Field(..., description="问题摘要", max_length=500)
    answer: str = Field(..., description="完整回答")


class FavoriteResponse(BaseModel):
    """收藏响应"""
    id: str
    user_id: str
    message_id: Optional[str]
    conversation_id: Optional[str]
    question: str
    answer: str
    created_at: str


@router.post("", summary="添加收藏")
async def create_favorite(
    request: FavoriteCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """添加收藏"""
    logger.info(f"添加收藏: user_id={request.user_id}, question={request.question[:30]}...")
    
    try:
        favorite = Favorite(
            user_id=request.user_id,
            message_id=request.message_id,
            conversation_id=request.conversation_id,
            question=request.question,
            answer=request.answer
        )
        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)
        
        return {
            "code": 0,
            "message": "success",
            "data": favorite.to_dict()
        }
    except Exception as e:
        logger.exception(f"添加收藏失败: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail={
            "code": 5001,
            "message": "添加收藏失败"
        })


@router.get("", summary="获取收藏列表")
async def get_favorites(
    user_id: str,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_async_session)
):
    """获取用户收藏列表，按时间倒序"""
    logger.info(f"获取收藏列表: user_id={user_id}, page={page}")
    
    try:
        # 查询总数
        count_stmt = select(Favorite).where(Favorite.user_id == user_id)
        count_result = await db.execute(count_stmt)
        total = len(count_result.scalars().all())
        
        # 分页查询
        offset = (page - 1) * page_size
        stmt = (
            select(Favorite)
            .where(Favorite.user_id == user_id)
            .order_by(desc(Favorite.created_at))
            .offset(offset)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        favorites = result.scalars().all()
        
        return {
            "code": 0,
            "message": "success",
            "data": {
                "items": [f.to_dict() for f in favorites],
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }
    except Exception as e:
        logger.exception(f"获取收藏列表失败: {e}")
        raise HTTPException(status_code=500, detail={
            "code": 5002,
            "message": "获取收藏列表失败"
        })


@router.delete("/{favorite_id}", summary="删除收藏")
async def delete_favorite(
    favorite_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """删除收藏"""
    logger.info(f"删除收藏: favorite_id={favorite_id}, user_id={user_id}")
    
    try:
        stmt = select(Favorite).where(
            Favorite.id == favorite_id,
            Favorite.user_id == user_id
        )
        result = await db.execute(stmt)
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            raise HTTPException(status_code=404, detail={
                "code": 4004,
                "message": "收藏不存在"
            })
        
        await db.delete(favorite)
        await db.commit()
        
        return {
            "code": 0,
            "message": "success",
            "data": {"id": favorite_id}
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"删除收藏失败: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail={
            "code": 5003,
            "message": "删除收藏失败"
        })
