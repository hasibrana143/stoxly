import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_create_portfolio_without_auth(client):
    response = client.post("/api/v1/portfolio/create", json={"name": "Test", "description": "Test portfolio"})
    assert response.status_code in [401, 403]


def test_list_portfolios_without_auth(client):
    response = client.get("/api/v1/portfolio/list")
    assert response.status_code in [401, 403]


def test_get_holdings_without_auth(client):
    response = client.get("/api/v1/portfolio/holdings")
    assert response.status_code in [401, 403]


def test_list_portfolios_with_bad_token(client):
    response = client.get("/api/v1/portfolio/list", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code in [401, 403]
