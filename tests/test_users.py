from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_user():
    response = client.post(
        "/users/",
        json={
            "telegram_id": 1001,
            "username": "test_user_1001",
            "first_name": "Test",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["telegram_id"] == 1001
    assert data["username"] == "test_user_1001"
    assert data["first_name"] == "Test"
    assert data["subscription_expires_at"] is None
    assert data["last_reminded_at"] is None
    assert data["created_at"] is not None
    assert data["updated_at"] is not None