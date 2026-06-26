from contextlib import contextmanager
import time

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

http_requests_total = Counter("stoxly_http_requests_total", "Total HTTP requests", ["method", "path", "status"])
http_request_duration_seconds = Histogram("stoxly_http_request_duration_seconds", "HTTP request duration", ["method", "path"], buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0))
active_requests = Gauge("stoxly_active_requests", "Active requests")
error_total = Counter("stoxly_errors_total", "Total errors", ["type", "path"])
db_query_duration = Histogram("stoxly_db_query_duration_seconds", "Database query duration", ["operation"], buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0))
external_api_duration = Histogram("stoxly_external_api_duration_seconds", "External API call duration", ["api_name"], buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0))


async def metrics_endpoint():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


def track_request(method: str, path: str, status: int, duration: float):
    http_requests_total.labels(method=method, path=path, status=status).inc()
    http_request_duration_seconds.labels(method=method, path=path).observe(duration)


def track_error(error_type: str, path: str):
    error_total.labels(type=error_type, path=path).inc()


@contextmanager
def track_db_query(operation: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        db_query_duration.labels(operation=operation).observe(time.perf_counter() - start)


@contextmanager
def track_external_api(api_name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        external_api_duration.labels(api_name=api_name).observe(time.perf_counter() - start)
