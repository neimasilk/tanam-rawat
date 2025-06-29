import pytest
from fastapi.testclient import TestClient

def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Tanam Rawat API"}

def test_register_user(client):
    response = client.post(
        "/register",
        json={"email": "newuser@example.com", "password": "newpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_login_user(client, test_user):
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_identify_endpoint_requires_auth(client):
    response = client.post("/identify")
    assert response.status_code == 401