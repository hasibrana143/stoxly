import time
import logging
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from core.redis_client import RedisRateLimiter, get_redis

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.fallback_limits: dict[str, list[float]] = defaultdict(list)
        self.redis_limiter: RedisRateLimiter | None = None

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            client_ip = request.client.host if request.client else "unknown"
            is_auth = "/auth/" in request.url.path
            max_req = 10 if is_auth else 100
            window = 60
            key = f"auth:{client_ip}" if is_auth else f"general:{client_ip}"

            if self.redis_limiter is None:
                redis = await get_redis()
                if redis:
                    self.redis_limiter = RedisRateLimiter(redis)

            if self.redis_limiter and self.redis_limiter.redis:
                blocked, _ = await self.redis_limiter.check_and_increment(key, max_req, window)
                if blocked:
                    raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
            else:
                now = time.time()
                limits = self.fallback_limits
                window_start = now - window
                limits[key] = [t for t in limits[key] if t > window_start]
                if len(limits[key]) >= max_req:
                    raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
                limits[key].append(now)

        response = await call_next(request)
        return response
