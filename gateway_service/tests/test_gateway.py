import os
import jwt
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SECRET_KEY = os.getenv("SECRET_KEY", "change_me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


def create_token(payload=None):
    payload = payload or {"sub": "user123"}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_auth_missing_token():
    response = client.get("/members/test")
    assert response.status_code == 403


def test_auth_invalid_token():
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/members/test", headers=headers)
    assert response.status_code == 401


def test_proxy_unknown_service(monkeypatch):
    token = create_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/unknown/foo", headers=headers)
    assert response.status_code == 404


def test_proxy_success(monkeypatch):
    token = create_token()
    headers = {"Authorization": f"Bearer {token}"}

    class DummyResponse:
        status_code = 200

        def json(self):
            return {"message": "pong"}

    class DummyClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def request(self, method, url, content=None, params=None, headers=None):
            return DummyResponse()

    monkeypatch.setattr("app.routes.proxy.httpx.AsyncClient", DummyClient)

    response = client.get("/members/anything", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "pong"}
