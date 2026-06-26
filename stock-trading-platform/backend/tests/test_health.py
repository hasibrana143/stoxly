import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_app_responds(client):
    response = client.get("/api/v1/stocks/search/TCS")
    assert response.status_code == 200


def test_unknown_route_returns_404(client):
    response = client.get("/api/v1/nonexistent/route")
    assert response.status_code == 404


def test_unknown_method_returns_405(client):
    # First get a CSRF token for the state-changing request
    csrf_resp = client.get("/api/v1/auth/csrf-token")
    csrf_token = csrf_resp.json()["csrf_token"]
    headers = {"X-CSRF-Token": csrf_token, "Cookie": f"csrf_token={csrf_token}"}
    response = client.put("/api/v1/stocks/search/TCS", headers=headers)
    assert response.status_code == 405
