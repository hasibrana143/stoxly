import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _register_and_login(client):
    resp = client.post("/api/v1/auth/register", json={
        "username": "testuser", "email": "test@example.com", "password": "TestPass123!",
    })
    if resp.status_code == 200:
        data = resp.json()
        return data["access_token"], data["user"]
    resp = client.post("/api/v1/auth/login", json={
        "email": "test@example.com", "password": "TestPass123!",
    })
    data = resp.json()
    return data["access_token"], data["user"]


def _get_csrf(client):
    resp = client.get("/api/v1/auth/csrf-token")
    token = resp.json()["csrf_token"]
    return token


def _auth_headers(token, csrf_token):
    return {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Token": csrf_token,
        "Cookie": f"csrf_token={csrf_token}",
    }


def test_create_alert_without_auth(client):
    response = client.post("/api/v1/alerts/", json={
        "symbol": "TCS", "target_price": 100.0, "condition": "above",
    })
    assert response.status_code in [401, 403]


def test_create_and_list_alerts(client):
    token, user = _register_and_login(client)

    csrf = _get_csrf(client)
    headers = _auth_headers(token, csrf)

    resp1 = client.post("/api/v1/alerts/", json={
        "symbol": "TCS", "target_price": 4500.0, "condition": "above",
    }, headers=headers)
    assert resp1.status_code == 200
    alert1_id = resp1.json()["alert"]["id"]

    csrf2 = _get_csrf(client)
    headers2 = _auth_headers(token, csrf2)

    resp2 = client.post("/api/v1/alerts/", json={
        "symbol": "RELIANCE", "target_price": 3000.0, "condition": "below",
    }, headers=headers2)
    assert resp2.status_code == 200
    alert2_id = resp2.json()["alert"]["id"]

    resp3 = client.get("/api/v1/alerts/", headers={"Authorization": f"Bearer {token}"})
    assert resp3.status_code == 200
    alerts = resp3.json()["alerts"]
    assert len(alerts) >= 2
    ids = [a["id"] for a in alerts]
    assert alert1_id in ids
    assert alert2_id in ids


def test_get_single_alert(client):
    token, user = _register_and_login(client)
    csrf = _get_csrf(client)
    headers = _auth_headers(token, csrf)

    resp = client.post("/api/v1/alerts/", json={
        "symbol": "INFY", "target_price": 2000.0, "condition": "above",
    }, headers=headers)
    alert_id = resp.json()["alert"]["id"]

    resp = client.get(f"/api/v1/alerts/{alert_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    alert = resp.json()["alert"]
    assert alert["id"] == alert_id
    assert alert["symbol"] == "INFY"
    assert alert["target_price"] == 2000.0


def test_update_alert(client):
    token, user = _register_and_login(client)
    csrf = _get_csrf(client)
    headers = _auth_headers(token, csrf)

    resp = client.post("/api/v1/alerts/", json={
        "symbol": "HDFC", "target_price": 1500.0, "condition": "above", "note": "initial",
    }, headers=headers)
    alert_id = resp.json()["alert"]["id"]

    csrf2 = _get_csrf(client)
    headers2 = _auth_headers(token, csrf2)

    resp = client.put(f"/api/v1/alerts/{alert_id}", json={
        "target_price": 1600.0, "condition": "below", "active": False, "note": "updated",
    }, headers=headers2)
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Alert updated"
    updated = data["alert"]
    assert updated["target_price"] == 1600.0
    assert updated["condition"] == "below"
    assert updated["active"] is False
    assert updated["note"] == "updated"


def test_delete_alert(client):
    token, user = _register_and_login(client)
    csrf = _get_csrf(client)
    headers = _auth_headers(token, csrf)

    resp = client.post("/api/v1/alerts/", json={
        "symbol": "WIPRO", "target_price": 500.0, "condition": "above",
    }, headers=headers)
    alert_id = resp.json()["alert"]["id"]

    csrf2 = _get_csrf(client)
    headers2 = _auth_headers(token, csrf2)

    resp = client.delete(f"/api/v1/alerts/{alert_id}", headers=headers2)
    assert resp.status_code == 200
    assert resp.json()["message"] == "Alert deleted"

    resp = client.get(f"/api/v1/alerts/{alert_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_check_alerts(client):
    token, user = _register_and_login(client)
    csrf = _get_csrf(client)
    headers = _auth_headers(token, csrf)

    resp = client.post("/api/v1/alerts/", json={
        "symbol": "TCS", "target_price": 100000.0, "condition": "below",
    }, headers=headers)
    assert resp.status_code == 200

    csrf2 = _get_csrf(client)
    headers2 = _auth_headers(token, csrf2)

    resp = client.post("/api/v1/alerts/check", headers=headers2)
    assert resp.status_code == 200
    data = resp.json()
    assert "triggered" in data
    triggered_symbols = [t["symbol"] for t in data["triggered"]]
    assert "TCS" in triggered_symbols
