from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import (
    get_cached_post,
    invalidate_cached_post,
    set_cached_post,
)
from app.database import get_db
from app.models import Post
from app.schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "", response_model=PostResponse, status_code=201,
)
async def create_post(
    body: PostCreate, db: AsyncSession = Depends(get_db),
):
    post = Post(title=body.title, content=body.content)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.get("", response_model=list[PostResponse])
async def list_posts(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Post)
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int, db: AsyncSession = Depends(get_db),
):
    cached = await get_cached_post(post_id)
    if cached is not None:
        return cached

    post = await db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    post_data = PostResponse.model_validate(post).model_dump(
        mode="json",
    )
    await set_cached_post(post_id, post_data)

    return post_data


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    body: PostUpdate,
    db: AsyncSession = Depends(get_db),
):
    post = await db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=400, detail="No fields to update",
        )

    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)
    await invalidate_cached_post(post_id)
    return post


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int, db: AsyncSession = Depends(get_db),
):
    post = await db.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.delete(post)
    await db.commit()
    await invalidate_cached_post(post_id)
