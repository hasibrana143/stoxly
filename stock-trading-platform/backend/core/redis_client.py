import redis.asyncio as aioredis
import logging

from core.config import settings

logger = logging.getLogger(__name__)

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        try:
            _redis = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            await _redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.warning(f"Redis unavailable, using fallback: {e}")
            _redis = None
    return _redis


async def close_redis():
    global _redis
    if _redis:
        await _redis.close()
        _redis = None


class RedisRateLimiter:
    def __init__(self, redis_client: aioredis.Redis | None):
        self.redis = redis_client

    async def check_and_increment(self, key: str, max_requests: int, window: int = 60) -> tuple[bool, int]:
        if not self.redis:
            return False, 0
        now = __import__("time").time()
        window_key = f"ratelimit:{key}:{int(now // window)}"
        count = await self.redis.incr(window_key)
        if count == 1:
            await self.redis.expire(window_key, window * 2)
        blocked = count > max_requests
        remaining = max(0, max_requests - count)
        return blocked, remaining
