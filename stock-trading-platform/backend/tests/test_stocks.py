from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_search_stocks():
    response = client.get("/api/v1/stocks/search/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert "stocks" in data
    assert len(data["stocks"]) > 0


def test_get_stock_price():
    response = client.get("/api/v1/stocks/price/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "RELIANCE"
    assert "current_price" in data
    assert "change_percent" in data


def test_get_stock_price_not_found():
    response = client.get("/api/v1/stocks/price/INVALID12345")
    assert response.status_code == 500


def test_market_movers():
    response = client.get("/api/v1/stocks/market-movers?type=gainers&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "stocks" in data
    assert len(data["stocks"]) <= 5
