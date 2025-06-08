
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db import get_db
from app.models import Base

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

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_and_list_feedback():
    r1 = client.post("/feedback/", json={"feedback": "Great team"})
    assert r1.status_code == 201
    data1 = r1.json()
    assert data1["feedback"] == "Great team"

    r2 = client.get("/feedback/")
    assert r2.status_code == 200
    items = r2.json()
    assert isinstance(items, list)
    assert len(items) == 1
    assert items[0]["feedback"] == "Great team"

def test_delete_feedback():
    client.post("/feedback/", json={"feedback": "To be deleted"})
    r_del = client.delete("/feedback/")
    assert r_del.status_code == 204

    r_list = client.get("/feedback/")
    assert r_list.status_code == 200
    assert r_list.json() == []
