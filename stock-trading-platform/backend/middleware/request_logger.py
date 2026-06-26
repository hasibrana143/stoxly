import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from core.logger import get_logger
from core.metrics import track_request, track_error, active_requests
from jose import jwt

logger = get_logger("middleware.request_logger")
EXEMPT_PATHS = {"/metrics", "/health", "/api/v1/health", "/docs", "/openapi.json", "/redoc"}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in EXEMPT_PATHS:
            return await call_next(request)

        method = request.method
        ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        request_id = getattr(request.state, "request_id", None)

        user = "anonymous"
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                claims = jwt.get_unverified_claims(auth_header[7:])
                user = claims.get("sub", "anonymous")
            except Exception:
                pass

        start = time.perf_counter()
        active_requests.inc()

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = (time.perf_counter() - start) * 1000
            active_requests.dec()
            track_error("unhandled_exception", path)
            logger.error(
                f"Unhandled exception: {exc}",
                extra={
                    "request_id": request_id,
                    "user": user,
                    "path": path,
                    "method": method,
                    "duration_ms": round(duration, 2),
                    "status": 500,
                },
            )
            raise

        duration = (time.perf_counter() - start) * 1000
        active_requests.dec()
        status_code = response.status_code

        track_request(method, path, status_code, duration / 1000)
        if status_code >= 500:
            track_error("server_error", path)
            logger.error(
                f"{method} {path} {status_code}",
                extra={
                    "request_id": request_id,
                    "user": user,
                    "path": path,
                    "method": method,
                    "status": status_code,
                    "duration_ms": round(duration, 2),
                    "ip": ip,
                    "user_agent": user_agent,
                },
            )
        elif status_code >= 400:
            logger.warning(
                f"{method} {path} {status_code}",
                extra={
                    "request_id": request_id,
                    "user": user,
                    "path": path,
                    "method": method,
                    "status": status_code,
                    "duration_ms": round(duration, 2),
                    "ip": ip,
                },
            )
        else:
            logger.info(
                f"{method} {path} {status_code}",
                extra={
                    "request_id": request_id,
                    "user": user,
                    "path": path,
                    "method": method,
                    "status": status_code,
                    "duration_ms": round(duration, 2),
                },
            )

        return response
