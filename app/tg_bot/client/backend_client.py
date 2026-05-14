import httpx

from app.tg_bot.config.config_reader import bot_settings


class BackendClientError(Exception):
    pass


async def get_user(telegram_id: int) -> dict | None:
    async with httpx.AsyncClient(base_url=bot_settings.backend_base_url) as client:
        response = await client.get(f"/users/{telegram_id}")

    if response.status_code == 200:
        return response.json()

    if response.status_code == 404:
        return None

    raise BackendClientError(
        f"Failed to get user. "
        f"Status: {response.status_code}, body: {response.text}"
    )


async def create_user(
    telegram_id: int,
    username: str | None,
    first_name: str | None,
) -> dict:
    async with httpx.AsyncClient(base_url=bot_settings.backend_base_url) as client:
        response = await client.post(
            "/users/",
            json={
                "telegram_id": telegram_id,
                "username": username,
                "first_name": first_name,
            },
        )

    if response.status_code == 201:
        return response.json()

    if response.status_code == 409:
        existing_user = await get_user(telegram_id)

        if existing_user is None:
            raise BackendClientError(
                "Backend returned 409, but user was not found after that."
            )

        return existing_user

    raise BackendClientError(
        f"Failed to create user. "
        f"Status: {response.status_code}, body: {response.text}"
    )


async def get_subscription_status(telegram_id: int) -> dict | None:
    async with httpx.AsyncClient(base_url=bot_settings.backend_base_url) as client:
        response = await client.get(f"/users/{telegram_id}/subscription-status")

    if response.status_code == 200:
        return response.json()

    if response.status_code == 404:
        return None

    raise BackendClientError(
        f"Failed to get subscription status. "
        f"Status: {response.status_code}, body: {response.text}"
    )


async def rebuild_subscription_reminders() -> dict:
    async with httpx.AsyncClient(base_url=bot_settings.backend_base_url) as client:
        response = await client.post("/subscription-reminders/rebuild")

    if response.status_code == 200:
        return response.json()

    raise BackendClientError(
        f"Failed to rebuild subscription reminders. "
        f"Status: {response.status_code}, body: {response.text}"
    )


async def get_due_subscription_reminders() -> list[dict]:
    async with httpx.AsyncClient(base_url=bot_settings.backend_base_url) as client:
        response = await client.get("/subscription-reminders/due")

    if response.status_code == 200:
        return response.json()

    raise BackendClientError(
        f"Failed to get due subscription reminders. "
        f"Status: {response.status_code}, body: {response.text}"
    )


async def delete_subscription_reminder(telegram_id: int) -> None:
    async with httpx.AsyncClient(base_url=bot_settings.backend_base_url) as client:
        response = await client.delete(f"/subscription-reminders/{telegram_id}")

    if response.status_code == 204:
        return

    raise BackendClientError(
        f"Failed to delete subscription reminder. "
        f"telegram_id={telegram_id}. "
        f"Status: {response.status_code}, body: {response.text}"
    )

async def create_mock_payment(telegram_id: int) -> dict | None:
    print("вызвали create_mock_payment")
    async with httpx.AsyncClient(base_url=bot_settings.backend_base_url) as client:
        response = await client.post(f"/payments/mock/{telegram_id}")

    if response.status_code == 200:
        return response.json()

    if response.status_code == 404:
        return None

    raise BackendClientError(
        f"Failed to create mock payment. "
        f"Status: {response.status_code}, body: {response.text}"
    )