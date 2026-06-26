from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_app_responds():
    response = client.get("/api/v1/stocks/search/TCS")
    assert response.status_code == 200


def test_unknown_route_returns_404():
    response = client.get("/api/v1/nonexistent/route")
    assert response.status_code == 404


def test_unknown_method_returns_405():
    response = client.put("/api/v1/stocks/search/TCS")
    assert response.status_code == 405
