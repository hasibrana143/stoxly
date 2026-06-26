import pytest
from unittest.mock import patch
from middleware.rate_limiter import RateLimitMiddleware
from middleware.ip_abuse import IPAbuseMiddleware


async def _noop_dispatch(self, request, call_next):
    return await call_next(request)


RateLimitMiddleware.dispatch = _noop_dispatch
IPAbuseMiddleware.dispatch = _noop_dispatch


@pytest.fixture(autouse=True)
def mock_captcha():
    with patch("api.v1.auth.verify_recaptcha", return_value=True):
        yield
