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
    return resp.json()["csrf_token"]


def _auth_headers(token, csrf_token):
    return {
        "Authorization": f"Bearer {token}",
        "X-CSRF-Token": csrf_token,
        "Cookie": f"csrf_token={csrf_token}",
    }


BASE = "/api/v1/chat/v2"


def test_chat_without_auth(client):
    response = client.post(f"{BASE}/message", json={"message": "What is TCS stock price?"})
    assert response.status_code in [401, 403]


def test_send_message_and_get_response(client):
    token, user = _register_and_login(client)
    csrf = _get_csrf(client)
    headers = _auth_headers(token, csrf)

    resp = client.post(f"{BASE}/message", json={
        "message": "What is TCS stock price?",
    }, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    assert len(data["suggestions"]) > 0
    assert "timestamp" in data


def test_get_chat_history(client):
    token, user = _register_and_login(client)
    csrf = _get_csrf(client)
    headers = _auth_headers(token, csrf)

    client.post(f"{BASE}/message", json={
        "message": "How is Nifty 50 performing?",
    }, headers=headers)

    resp = client.get(f"{BASE}/history", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "messages" in data
    messages = data["messages"]
    assert len(messages) > 0
    assert any(m.get("message") == "How is Nifty 50 performing?" for m in messages)
    assert data["total"] >= 1


def test_get_chat_history_with_limit(client):
    token, user = _register_and_login(client)

    for i in range(3):
        csrf = _get_csrf(client)
        headers = _auth_headers(token, csrf)
        client.post(f"{BASE}/message", json={
            "message": f"Test message {i}",
        }, headers=headers)

    resp = client.get(f"{BASE}/history?limit=2", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["messages"]) == 2
    assert data["total"] == 2


def test_delete_chat_history(client):
    token, user = _register_and_login(client)
    csrf = _get_csrf(client)
    headers = _auth_headers(token, csrf)

    client.post(f"{BASE}/message", json={
        "message": "What are today's top gainers?",
    }, headers=headers)

    csrf2 = _get_csrf(client)
    headers2 = _auth_headers(token, csrf2)
    resp = client.delete(f"{BASE}/history", headers=headers2)
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"

    resp = client.get(f"{BASE}/history", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["messages"]) == 0
    assert data["total"] == 0


def test_get_suggestions(client):
    resp = client.get(f"{BASE}/suggestions")
    assert resp.status_code == 200
    data = resp.json()
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)
    assert len(data["suggestions"]) > 0
    assert all(isinstance(s, str) for s in data["suggestions"])
    assert data["context"] == "general"
