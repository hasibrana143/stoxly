import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _register_and_login(client, suffix):
    resp = client.post("/api/v1/auth/register", json={
        "username": f"ptuser_{suffix}",
        "email": f"pt_{suffix}@example.com",
        "password": "TestPass123!"
    })
    data = resp.json()
    return data["access_token"], data["user"]


def _get_csrf(client):
    resp = client.get("/api/v1/auth/csrf-token")
    token = resp.json()["csrf_token"]
    return token


def test_get_account_without_auth(client):
    response = client.get("/api/v1/paper-trading/account")
    assert response.status_code in [401, 403]


def test_get_account_creates_if_not_exists(client):
    token, _ = _register_and_login(client, 1)
    response = client.get(
        "/api/v1/paper-trading/account",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == 1000000.0
    assert data["initial_balance"] == 1000000.0


def test_buy_stock(client):
    token, _ = _register_and_login(client, 2)
    csrf_token = _get_csrf(client)
    client.cookies.set("csrf_token", csrf_token)
    response = client.post(
        "/api/v1/paper-trading/buy",
        json={"symbol": "TCS", "quantity": 10},
        headers={
            "Authorization": f"Bearer {token}",
            "X-CSRF-Token": csrf_token
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["transaction"]["symbol"] == "TCS"
    assert data["transaction"]["quantity"] == 10
    holdings_resp = client.get(
        "/api/v1/paper-trading/holdings",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert holdings_resp.status_code == 200
    hdata = holdings_resp.json()
    assert hdata["count"] == 1
    assert hdata["holdings"][0]["symbol"] == "TCS"
    assert hdata["holdings"][0]["quantity"] == 10


def test_sell_stock(client):
    token, _ = _register_and_login(client, 3)
    csrf_token = _get_csrf(client)
    client.cookies.set("csrf_token", csrf_token)
    headers = {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Token": csrf_token
    }
    buy_resp = client.post(
        "/api/v1/paper-trading/buy",
        json={"symbol": "TCS", "quantity": 10},
        headers=headers
    )
    assert buy_resp.status_code == 200
    sell_resp = client.post(
        "/api/v1/paper-trading/sell",
        json={"symbol": "TCS", "quantity": 5},
        headers=headers
    )
    assert sell_resp.status_code == 200
    sdata = sell_resp.json()
    assert sdata["transaction"]["symbol"] == "TCS"
    assert sdata["transaction"]["quantity"] == -5
    holdings_resp = client.get(
        "/api/v1/paper-trading/holdings",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert holdings_resp.status_code == 200
    hdata = holdings_resp.json()
    assert hdata["count"] == 1
    assert hdata["holdings"][0]["symbol"] == "TCS"
    assert hdata["holdings"][0]["quantity"] == 5


def test_sell_more_than_held(client):
    token, _ = _register_and_login(client, 4)
    csrf_token = _get_csrf(client)
    client.cookies.set("csrf_token", csrf_token)
    response = client.post(
        "/api/v1/paper-trading/sell",
        json={"symbol": "TCS", "quantity": 1},
        headers={
            "Authorization": f"Bearer {token}",
            "X-CSRF-Token": csrf_token
        }
    )
    assert response.status_code == 400


def test_buy_insufficient_balance(client):
    token, _ = _register_and_login(client, 5)
    csrf_token = _get_csrf(client)
    client.cookies.set("csrf_token", csrf_token)
    response = client.post(
        "/api/v1/paper-trading/buy",
        json={"symbol": "TCS", "quantity": 100000},
        headers={
            "Authorization": f"Bearer {token}",
            "X-CSRF-Token": csrf_token
        }
    )
    assert response.status_code == 400


def test_get_holdings(client):
    token, _ = _register_and_login(client, 6)
    csrf_token = _get_csrf(client)
    client.cookies.set("csrf_token", csrf_token)
    headers = {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Token": csrf_token
    }
    client.post(
        "/api/v1/paper-trading/buy",
        json={"symbol": "TCS", "quantity": 5},
        headers=headers
    )
    holdings_resp = client.get(
        "/api/v1/paper-trading/holdings",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert holdings_resp.status_code == 200
    data = holdings_resp.json()
    assert data["count"] >= 1
    assert any(h["symbol"] == "TCS" for h in data["holdings"])


def test_get_transactions(client):
    token, _ = _register_and_login(client, 7)
    csrf_token = _get_csrf(client)
    client.cookies.set("csrf_token", csrf_token)
    headers = {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Token": csrf_token
    }
    client.post(
        "/api/v1/paper-trading/buy",
        json={"symbol": "TCS", "quantity": 10},
        headers=headers
    )
    client.post(
        "/api/v1/paper-trading/sell",
        json={"symbol": "TCS", "quantity": 3},
        headers=headers
    )
    txn_resp = client.get(
        "/api/v1/paper-trading/transactions",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert txn_resp.status_code == 200
    data = txn_resp.json()
    assert data["count"] >= 2
    assert any(t["symbol"] == "TCS" and t["type"] == "buy" for t in data["transactions"])
    assert any(t["symbol"] == "TCS" and t["type"] == "sell" for t in data["transactions"])


def test_reset_account(client):
    token, _ = _register_and_login(client, 8)
    csrf_token = _get_csrf(client)
    client.cookies.set("csrf_token", csrf_token)
    headers = {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Token": csrf_token
    }
    client.post(
        "/api/v1/paper-trading/buy",
        json={"symbol": "TCS", "quantity": 5},
        headers=headers
    )
    reset_resp = client.post(
        "/api/v1/paper-trading/reset",
        headers=headers
    )
    assert reset_resp.status_code == 200
    rdata = reset_resp.json()
    assert rdata["balance"] == 1000000.0
    account_resp = client.get(
        "/api/v1/paper-trading/account",
        headers={"Authorization": f"Bearer {token}"}
    )
    adata = account_resp.json()
    assert adata["balance"] == 1000000.0
    assert adata["holdings_count"] == 0
    assert adata["transaction_count"] == 0


def test_leaderboard(client):
    token, _ = _register_and_login(client, 9)
    csrf_token = _get_csrf(client)
    client.cookies.set("csrf_token", csrf_token)
    client.post(
        "/api/v1/paper-trading/buy",
        json={"symbol": "TCS", "quantity": 5},
        headers={
            "Authorization": f"Bearer {token}",
            "X-CSRF-Token": csrf_token
        }
    )
    response = client.get("/api/v1/paper-trading/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    assert "leaderboard" in data
