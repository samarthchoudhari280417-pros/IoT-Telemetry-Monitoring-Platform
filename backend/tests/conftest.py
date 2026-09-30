"""Pytest fixtures: isolated SQLite DB + FastAPI TestClient for each test."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    # StaticPool ensures every connection shares the SAME in-memory SQLite DB
    # instead of each checkout creating a fresh, empty database.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session, monkeypatch):
    # Prevent the real MQTT client from trying to connect during tests.
    # app.main imported these names directly, so patch them there.
    from app import main as main_module
    monkeypatch.setattr(main_module, "start_mqtt_client", lambda: None)
    monkeypatch.setattr(main_module, "stop_mqtt_client", lambda: None)

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
