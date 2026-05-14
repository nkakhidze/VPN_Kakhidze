from datetime import datetime


def create_user(client, telegram_id=1001, username="test_user", first_name="Test"):
    return client.post(
        "/users/",
        json={
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
        },
    )


def test_create_mock_payment_for_existing_user(client):
    create_user(client, telegram_id=1001)

    response = client.post("/payments/mock/1001")

    assert response.status_code == 200

    data = response.json()

    payment = data["payment"]

    assert payment["telegram_id"] == 1001
    assert payment["amount"] == 300
    assert payment["currency"] == "RUB"
    assert payment["status"] == "succeeded"
    assert payment["provider"] == "mock"
    assert payment["paid_at"] is not None

    assert data["subscription_expires_at"] is not None


def test_mock_payment_extends_subscription(client):
    create_user(client, telegram_id=1001)

    response = client.post("/payments/mock/1001")

    assert response.status_code == 200

    data = response.json()

    expires_at = datetime.fromisoformat(data["subscription_expires_at"])

    assert expires_at > datetime.utcnow()

def test_create_mock_payment_for_not_existing_user_returns_404(client):
    response = client.post("/payments/mock/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"