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
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_create_and_list_members():
    payload1 = {
        "first_name": "John",
        "last_name": "Doe",
        "login": "john123",
        "avatar_url": "https://example.com/avatar.jpg",
        "followers": 120,
        "following": 35,
        "title": "Senior Developer",
        "email": "john@example.com"
    }
    r1 = client.post("/members/", json=payload1)
    assert r1.status_code == 201
    data1 = r1.json()
    assert data1["login"] == "john123"

    payload2 = {
        "first_name": "Jane",
        "last_name": "Smith",
        "login": "jane456",
        "avatar_url": "https://example.com/avatar2.jpg",
        "followers": 80,
        "following": 20,
        "title": "Developer",
        "email": "jane@example.com"
    }
    client.post("/members/", json=payload2)

    r2 = client.get("/members/")
    assert r2.status_code == 200
    items = r2.json()
    assert len(items) == 2
    assert items[0]["followers"] >= items[1]["followers"]

def test_delete_members():
    payload = {
        "first_name": "Alice",
        "last_name": "Wonder",
        "login": "alice789",
        "avatar_url": "https://example.com/avatar3.jpg",
        "followers": 50,
        "following": 10,
        "title": "Junior Dev",
        "email": "alice@example.com"
    }
    client.post("/members/", json=payload)

    r_del = client.delete("/members/")
    assert r_del.status_code == 204

    r_list = client.get("/members/")
    assert r_list.status_code == 200
    assert r_list.json() == []
