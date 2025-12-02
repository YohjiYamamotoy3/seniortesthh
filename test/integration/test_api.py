import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.main import app
from src.database import get_db
from test.conftest import override_get_db


@pytest.fixture
def client(db_session, override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_register_user(client):
    response = client.post(
        "/api/v1/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "test user"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "test user"
    assert "id" in data


def test_register_duplicate_user(client):
    client.post(
        "/api/v1/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "test user"
        }
    )
    response = client.post(
        "/api/v1/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "test user"
        }
    )
    assert response.status_code == 409


def test_login(client):
    client.post(
        "/api/v1/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "test user"
        }
    )
    response = client.post(
        "/api/v1/login",
        params={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_create_organization(client):
    client.post(
        "/api/v1/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "test user"
        }
    )
    login_response = client.post(
        "/api/v1/login",
        params={"email": "test@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    response = client.post(
        "/api/v1/organizations",
        json={"name": "test org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test org"
    assert "id" in data


def test_create_contact(client):
    client.post(
        "/api/v1/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "test user"
        }
    )
    login_response = client.post(
        "/api/v1/login",
        params={"email": "test@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "test org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]
    response = client.post(
        "/api/v1/contacts",
        json={
            "name": "john doe",
            "email": "john@example.com",
            "phone": "1234567890"
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": org_id
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "john doe"
    assert data["email"] == "john@example.com"


def test_create_deal(client):
    client.post(
        "/api/v1/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "test user"
        }
    )
    login_response = client.post(
        "/api/v1/login",
        params={"email": "test@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "test org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]
    contact_response = client.post(
        "/api/v1/contacts",
        json={
            "name": "john doe",
            "email": "john@example.com"
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": org_id
        }
    )
    contact_id = contact_response.json()["id"]
    response = client.post(
        "/api/v1/deals",
        json={
            "contact_id": contact_id,
            "title": "test deal",
            "value": 1000.0,
            "stage": "new"
        },
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": org_id
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "test deal"
    assert data["value"] == 1000.0
    assert data["stage"] == "new"


def test_get_analytics_summary(client):
    client.post(
        "/api/v1/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "test user"
        }
    )
    login_response = client.post(
        "/api/v1/login",
        params={"email": "test@example.com", "password": "password123"}
    )
    token = login_response.json()["access_token"]
    org_response = client.post(
        "/api/v1/organizations",
        json={"name": "test org"},
        headers={"Authorization": f"Bearer {token}"}
    )
    org_id = org_response.json()["id"]
    response = client.get(
        "/api/v1/analytics/deals/summary",
        headers={
            "Authorization": f"Bearer {token}",
            "X-Organization-Id": org_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "total_value" in data
    assert "avg_value" in data

