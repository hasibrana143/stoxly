import uuid
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def csrf_token(client):
    response = client.get("/api/v1/auth/csrf-token")
    assert response.status_code == 200
    body = response.json()
    assert "csrf_token" in body
    csrf = body["csrf_token"]
    assert response.cookies.get("csrf_token") == csrf
    return csrf


def test_csrf_token_endpoint(client):
    response = client.get("/api/v1/auth/csrf-token")
    assert response.status_code == 200
    body = response.json()
    assert "csrf_token" in body
    assert len(body["csrf_token"]) > 0
    set_cookie = response.headers.get("set-cookie", "")
    assert "csrf_token=" in set_cookie


def test_csrf_blocks_state_changing_without_token(client):
    response = client.post(
        "/api/v1/portfolio/create",
        json={"name": "test", "description": "test"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "CSRF validation failed"


def test_csrf_allows_with_valid_token(client, csrf_token):
    response = client.post(
        "/api/v1/portfolio/create",
        json={"name": "test", "description": "test"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code in (401, 403)
    assert response.json()["detail"] != "CSRF validation failed"


def test_logout_blacklists_token(client):
    email = f"logout_{uuid.uuid4().hex[:8]}@test.com"
    username = f"logout_user_{uuid.uuid4().hex[:8]}"
    register_resp = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": "StrongPass1"},
    )
    assert register_resp.status_code == 200
    token = register_resp.json()["access_token"]
    auth_header = {"Authorization": f"Bearer {token}"}

    list_resp = client.get("/api/v1/portfolio/list", headers=auth_header)
    assert list_resp.status_code == 200

    logout_resp = client.post("/api/v1/auth/logout", headers=auth_header)
    assert logout_resp.status_code == 200
    assert logout_resp.json()["message"] == "Logged out successfully"

    reused_resp = client.get("/api/v1/portfolio/list", headers=auth_header)
    assert reused_resp.status_code == 401
    assert "revoked" in reused_resp.json()["detail"].lower()


def test_logout_all_returns_message(client):
    email = f"logoutall_{uuid.uuid4().hex[:8]}@test.com"
    username = f"logoutall_user_{uuid.uuid4().hex[:8]}"
    register_resp = client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": "StrongPass1"},
    )
    assert register_resp.status_code == 200
    token = register_resp.json()["access_token"]

    response = client.post(
        "/api/v1/auth/logout-all",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_rate_limiter_headers(client):
    for _ in range(5):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        if "X-RateLimit-Limit" in response.headers:
            assert int(response.headers["X-RateLimit-Limit"]) > 0


def test_security_headers_present(client):
    response = client.get("/api/v1/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Content-Security-Policy") is not None
    assert response.headers.get("X-Request-ID") is not None
    assert response.headers.get("Strict-Transport-Security") is not None
    assert response.headers.get("X-XSS-Protection") is not None
    assert response.headers.get("Referrer-Policy") is not None
    assert response.headers.get("Permissions-Policy") is not None


def test_request_body_too_large(client):
    large_body = "x" * (1_048_576 + 1)
    response = client.post(
        "/api/v1/auth/login",
        json={"data": large_body},
    )
    assert response.status_code == 413
    assert "too large" in response.json()["detail"].lower()


def test_register_weak_password(client):
    weak_passwords = [
        "short",
        "nouppercase1",
        "ALLUPPERCASE1",
        "NoDigits!",
    ]
    for pwd in weak_passwords:
        email = f"weak_{uuid.uuid4().hex[:8]}@test.com"
        username = f"weak_user_{uuid.uuid4().hex[:8]}"
        response = client.post(
            "/api/v1/auth/register",
            json={"username": username, "email": email, "password": pwd},
        )
        assert response.status_code == 400


def test_register_duplicate_email(client):
    email = f"dup_{uuid.uuid4().hex[:8]}@test.com"
    username1 = f"dup_user1_{uuid.uuid4().hex[:8]}"
    resp1 = client.post(
        "/api/v1/auth/register",
        json={"username": username1, "email": email, "password": "StrongPass1"},
    )
    assert resp1.status_code == 200

    username2 = f"dup_user2_{uuid.uuid4().hex[:8]}"
    resp2 = client.post(
        "/api/v1/auth/register",
        json={"username": username2, "email": email, "password": "StrongPass2"},
    )
    assert resp2.status_code == 400
    assert resp2.json()["detail"] == "Email already registered"
