import logging

import sentry_sdk
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.audit import audit_log

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    if isinstance(exc, StarletteHTTPException):
        if exc.status_code in (401, 403):
            audit_log("security.unauthorized_access", ip=request.client.host if request.client else "unknown", details={"path": str(request.url.path), "method": request.method, "status": exc.status_code})
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail, "request_id": request_id})
    sentry_sdk.capture_exception(exc)
    logger.error(f"Request {request_id} - Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error. Please try again later.", "request_id": request_id})
