from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import get_db
from app.db.models import User, SubscriptionReminder
from app.main import app


BASE_DIR = Path(__file__).resolve().parents[1]
ENV_TEST_FILE = BASE_DIR / ".env.test"


class TestSettings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int

    model_config = SettingsConfigDict(
        env_file=ENV_TEST_FILE,
        env_file_encoding="utf-8",
    )

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


test_settings = TestSettings()

test_engine = create_engine(test_settings.database_url)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_test_db


@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    alembic_cfg = Config(str(BASE_DIR / "alembic.ini"))
    alembic_cfg.attributes["database_url"] = test_settings.database_url

    command.upgrade(alembic_cfg, "head")


@pytest.fixture(autouse=True)
def clean_users(apply_migrations):
    db = TestingSessionLocal()

    try:
        db.query(SubscriptionReminder).delete()
        db.query(User).delete()
        db.commit()
        yield
    finally:
        db.query(SubscriptionReminder).delete()
        db.query(User).delete()
        db.commit()
        db.close()


@pytest.fixture()
def client():
    return TestClient(app)