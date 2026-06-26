import re

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from core.audit import audit_log


EXEMPT_PATHS = re.compile(
    r"^/(api/v1/auth/|health|docs|openapi\.json|redoc|api/v1/health)"
)

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})

STATE_CHANGING_METHODS = frozenset({"POST", "PUT", "DELETE", "PATCH"})


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method

        if not path.startswith("/api/"):
            return await call_next(request)

        if method in SAFE_METHODS:
            return await call_next(request)

        if EXEMPT_PATHS.match(path):
            return await call_next(request)

        if method in STATE_CHANGING_METHODS:
            csrf_cookie = request.cookies.get("csrf_token")
            csrf_header = request.headers.get("X-CSRF-Token")

            if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
                audit_log("security.csrf_failure", ip=request.client.host if request.client else "unknown", details={"path": path, "method": method})
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF validation failed"},
                )

        return await call_next(request)
