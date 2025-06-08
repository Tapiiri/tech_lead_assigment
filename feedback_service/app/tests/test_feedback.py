# feedback_service/app/tests/test_feedback.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_db
from app.models import Base

# --- Configure an in-memory SQLite DB that persists across sessions ---
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create tables once for the in-memory database
Base.metadata.create_all(bind=engine)

# --- Override get_db dependency to use our TestingSessionLocal ---
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# --- Fixture to reset the database before each test ---
@pytest.fixture(autouse=True)
def clear_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

# --- Tests ---

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_and_list_feedback():
    # Create a new feedback entry
    r1 = client.post("/feedback/", json={"feedback": "Great team"})
    assert r1.status_code == 201
    data1 = r1.json()
    assert data1["feedback"] == "Great team"

    # List feedback entries
    r2 = client.get("/feedback/")
    assert r2.status_code == 200
    items = r2.json()
    assert isinstance(items, list)
    assert len(items) == 1
    assert items[0]["feedback"] == "Great team"

def test_delete_feedback():
    # Seed one record
    client.post("/feedback/", json={"feedback": "To be deleted"})
    # Soft-delete all feedback
    r_del = client.delete("/feedback/")
    assert r_del.status_code == 204

    # Ensure the list is empty
    r_list = client.get("/feedback/")
    assert r_list.status_code == 200
    assert r_list.json() == []
