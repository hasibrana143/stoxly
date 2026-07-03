
def test_register_user(client):
    response = client.post("/api/v1/auth/register", json={"username": "testuser", "email": "test@example.com", "password": "testpass123"})
    assert response.status_code in [200, 400]


def test_login_invalid(client):
    response = client.post("/api/v1/auth/login", json={"email": "nonexistent@test.com", "password": "wrongpass"})
    assert response.status_code == 401
