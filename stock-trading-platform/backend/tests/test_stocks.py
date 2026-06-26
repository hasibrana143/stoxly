import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_search_stocks(client):
    response = client.get("/api/v1/stocks/search/TCS")
    assert response.status_code == 200
    data = response.json()
    assert "stocks" in data


def test_get_stock_price(client):
    response = client.get("/api/v1/stocks/price/TCS")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "TCS"


def test_get_stock_price_not_found(client):
    response = client.get("/api/v1/stocks/price/INVALID12345")
    assert response.status_code == 404


def test_market_movers(client):
    response = client.get("/api/v1/stocks/market-movers?type=gainers&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "stocks" in data
