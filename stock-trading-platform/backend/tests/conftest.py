import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from middleware.rate_limiter import RateLimitMiddleware
from middleware.ip_abuse import IPAbuseMiddleware
from main import app
from core.database import Base, get_db


async def _noop_dispatch(self, request, call_next):
    return await call_next(request)


RateLimitMiddleware.dispatch = _noop_dispatch
IPAbuseMiddleware.dispatch = _noop_dispatch


test_engine = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_db():
    yield
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def mock_captcha():
    with patch("api.v1.auth.verify_recaptcha", return_value=True):
        yield
