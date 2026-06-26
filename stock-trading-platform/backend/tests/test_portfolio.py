from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_create_portfolio_without_auth():
    response = client.post("/api/v1/portfolio/create", json={
        "name": "Test Portfolio",
        "description": "A test portfolio"
    })
    assert response.status_code == 401


def test_list_portfolios_without_auth():
    response = client.get("/api/v1/portfolio/list")
    assert response.status_code == 401


def test_get_holdings_without_auth():
    response = client.get("/api/v1/portfolio/holdings")
    assert response.status_code == 401


def test_list_portfolios_with_bad_token():
    response = client.get(
        "/api/v1/portfolio/list",
        headers={"Authorization": "Bearer invalid_token_here"}
    )
    assert response.status_code in [401, 403]
