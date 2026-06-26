from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_user():
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code in [200, 400]


def test_login_invalid():
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401
