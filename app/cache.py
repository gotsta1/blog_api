import json
import logging

from redis.exceptions import RedisError

from app.config import settings
from app.redis import redis_client

logger = logging.getLogger(__name__)

CACHE_PREFIX = "post"


def _key(post_id: int) -> str:
    return f"{CACHE_PREFIX}:{post_id}"


async def get_cached_post(post_id: int) -> dict | None:
    try:
        data = await redis_client.get(_key(post_id))
        if data is None:
            return None
        return json.loads(data)
    except RedisError:
        logger.warning(
            "Redis unavailable, cache miss for post %s",
            post_id,
        )
        return None


async def set_cached_post(
    post_id: int, post_data: dict,
) -> None:
    try:
        await redis_client.set(
            _key(post_id),
            json.dumps(post_data, default=str),
            ex=settings.cache_ttl,
        )
    except RedisError:
        logger.warning(
            "Redis unavailable, skipping cache set for post %s",
            post_id,
        )


async def invalidate_cached_post(post_id: int) -> None:
    try:
        await redis_client.delete(_key(post_id))
    except RedisError:
        logger.warning(
            "Redis unavailable, skipping invalidation for post %s",
            post_id,
        )
