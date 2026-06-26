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
    response = client.put("/api/v1/stocks/search/TCS")
    assert response.status_code == 405
