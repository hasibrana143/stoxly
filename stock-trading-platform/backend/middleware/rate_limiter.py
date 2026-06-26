import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.general_limits: dict[str, list[float]] = defaultdict(list)
        self.auth_limits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/"):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()

            is_auth = "/auth/" in request.url.path
            limits = self.auth_limits if is_auth else self.general_limits
            max_req = 10 if is_auth else 100
            window = 60

            window_start = now - window
            limits[client_ip] = [t for t in limits[client_ip] if t > window_start]

            if len(limits[client_ip]) >= max_req:
                raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")

            limits[client_ip].append(now)

        response = await call_next(request)
        return response
