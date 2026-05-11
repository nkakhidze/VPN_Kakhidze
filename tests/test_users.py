from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_user(client, telegram_id=1001, username="test_user", first_name="Test"):
    """helper-функция для JSON при создании"""
    return client.post(
        "/users/",
        json={
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
        },
    )


def test_create_user(client):
    response = create_user(client)

    assert response.status_code == 201

    data = response.json()

    assert data["telegram_id"] == 1001
    assert data["username"] == "test_user"
    assert data["first_name"] == "Test"
    assert data["subscription_expires_at"] is None
    assert data["last_reminded_at"] is None
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_create_user_with_existing_telegram_id_returns_409(client):
    create_user(client, telegram_id=1001)

    response = create_user(client, telegram_id=1001)

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this telegram_id already exists"


def test_get_users(client):
    create_user(client, telegram_id=1001, username="user_1", first_name="User 1")
    create_user(client, telegram_id=1002, username="user_2", first_name="User 2")

    response = client.get("/users/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["telegram_id"] == 1001
    assert data[1]["telegram_id"] == 1002


def test_get_user_by_telegram_id(client):
    create_user(client, telegram_id=1001)

    response = client.get("/users/1001")

    assert response.status_code == 200

    data = response.json()

    assert data["telegram_id"] == 1001
    assert data["username"] == "test_user"
    assert data["first_name"] == "Test"


def test_get_not_existing_user_returns_404(client):
    response = client.get("/users/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_update_user(client):
    create_user(client, telegram_id=1001)

    response = client.patch(
        "/users/1001",
        json={
            "username": "updated_user",
            "first_name": "Updated",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["telegram_id"] == 1001
    assert data["username"] == "updated_user"
    assert data["first_name"] == "Updated"


def test_update_not_existing_user_returns_404(client):
    response = client.patch(
        "/users/9999",
        json={
            "username": "updated_user",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user(client):
    create_user(client, telegram_id=1001)

    delete_response = client.delete("/users/1001")

    assert delete_response.status_code == 204

    get_response = client.get("/users/1001")

    assert get_response.status_code == 404
    assert get_response.json()["detail"] == "User not found"


def test_delete_not_existing_user_returns_404(client):
    response = client.delete("/users/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_extend_subscription_for_user_without_subscription(client):
    create_response = create_user(client, telegram_id=1001)

    create_data = create_response.json()

    assert create_response.status_code == 201
    assert create_data["subscription_expires_at"] is None

    extend_response = client.post("/users/1001/extend-subscription")

    assert extend_response.status_code == 200

    extend_data = extend_response.json()

    assert extend_data["telegram_id"] == 1001
    assert extend_data["subscription_expires_at"] is not None


def test_extend_subscription_for_user_without_subscription_sets_30_days(client):
    create_user(client, telegram_id=1001)

    before_request = datetime.now()

    response = client.post("/users/1001/extend-subscription")

    after_request = datetime.now()

    assert response.status_code == 200

    data = response.json()
    expires_at = datetime.fromisoformat(data["subscription_expires_at"])

    assert before_request + timedelta(days=30) <= expires_at
    assert expires_at <= after_request + timedelta(days=30)


def test_extend_active_subscription_adds_30_days_to_current_expiration(client):
    create_user(client, telegram_id=1001)

    first_response = client.post("/users/1001/extend-subscription")

    assert first_response.status_code == 200

    first_data = first_response.json()
    first_expires_at = datetime.fromisoformat(first_data["subscription_expires_at"])

    second_response = client.post("/users/1001/extend-subscription")

    assert second_response.status_code == 200

    second_data = second_response.json()
    second_expires_at = datetime.fromisoformat(second_data["subscription_expires_at"])

    assert second_expires_at == first_expires_at + timedelta(days=30)


def test_extend_expired_subscription_sets_30_days_from_now(client):
    create_user(client, telegram_id=1001)

    client.patch(
        "/users/1001",
        json={
            "subscription_expires_at": "2020-01-01T00:00:00"
        },
    )

    before_request = datetime.utcnow()

    response = client.post("/users/1001/extend-subscription")

    after_request = datetime.utcnow()

    assert response.status_code == 200

    data = response.json()
    expires_at = datetime.fromisoformat(data["subscription_expires_at"])

    assert before_request + timedelta(days=30) <= expires_at
    assert expires_at <= after_request + timedelta(days=30)


def test_extend_expired_subscription_sets_30_days_from_now(client):
    create_user(client, telegram_id=1001)

    client.patch(
        "/users/1001",
        json={
            "subscription_expires_at": "2020-01-01T00:00:00"
        },
    )

    before_request = datetime.now()

    response = client.post("/users/1001/extend-subscription")

    after_request = datetime.now()

    assert response.status_code == 200

    data = response.json()
    expires_at = datetime.fromisoformat(data["subscription_expires_at"])

    assert before_request + timedelta(days=30) <= expires_at
    assert expires_at <= after_request + timedelta(days=30)


def test_extend_subscription_for_not_existing_user_returns_404(client):
    response = client.post("/users/9999/extend-subscription")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


