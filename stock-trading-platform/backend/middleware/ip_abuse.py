import time
from collections import defaultdict
from typing import Dict

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from core.audit import audit_log
from core.config import settings


class IPAbuseMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._request_counts: Dict[str, list] = defaultdict(list)
        self._blocked_ips: Dict[str, float] = {}
        self._cleanup_counter = 0
        self._whitelist = {"127.0.0.1", "::1", "localhost"}

        self._exempt_paths = {"/health", "/docs", "/openapi.json", "/redoc"}
        self._threshold = settings.IP_ABUSE_THRESHOLD
        self._window = settings.IP_ABUSE_WINDOW
        self._block_duration = settings.IP_ABUSE_BLOCK_DURATION

    async def dispatch(self, request: Request, call_next):
        if request.url.path in self._exempt_paths:
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"

        if ip in self._whitelist:
            return await call_next(request)

        now = time.time()

        if ip in self._blocked_ips:
            if now - self._blocked_ips[ip] < self._block_duration:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Your IP has been temporarily blocked."},
                )
            del self._blocked_ips[ip]

        self._request_counts[ip].append(now)

        window_start = now - self._window
        self._request_counts[ip] = [t for t in self._request_counts[ip] if t > window_start]

        if len(self._request_counts[ip]) > self._threshold:
            self._blocked_ips[ip] = now
            del self._request_counts[ip]
            audit_log("security.ip_blocked", ip=ip, details={"threshold": self._threshold, "window": self._window})
            print(f"[SECURITY] IP {ip} blocked for exceeding threshold")
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Your IP has been temporarily blocked."},
            )

        self._cleanup_counter += 1
        if self._cleanup_counter > 100:
            self._cleanup_counter = 0
            self._cleanup_stale_entries()

        return await call_next(request)

    def _cleanup_stale_entries(self):
        cutoff = time.time() - self._window
        stale_ips = [
            ip for ip, timestamps in self._request_counts.items()
            if not any(t > cutoff for t in timestamps)
        ]
        for ip in stale_ips:
            del self._request_counts[ip]
