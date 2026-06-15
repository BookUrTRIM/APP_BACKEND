import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")
os.environ.setdefault("DOCS_ENABLED", "0")
os.environ.setdefault("STRIPE_SECRET_KEY", "")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import shared.db as db_module
from shared.db import Base

# Import all DAOs to ensure they are registered in Base.metadata
import daos.user_account_dao
import daos.client_dao
import daos.client_hair_profile_dao
import daos.provider_dao
import daos.service_dao
import daos.service_question_dao
import daos.availability_dao
import daos.appointment_dao
import daos.appointment_service_dao
import daos.payment_dao
import daos.receipt_dao
import daos.invoice_dao
import daos.review_dao
import daos.notification_dao

_test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
db_module.engine = _test_engine
db_module.SessionLocal = sessionmaker(bind=_test_engine)


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(_test_engine)
    yield
    Base.metadata.drop_all(_test_engine)


@pytest.fixture
def client(reset_db):
    from app import create_app
    app = create_app()
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ── Auth helpers ──────────────────────────────────────────────────────────────

def _activate_account(email: str) -> None:
    """Active un compte directement en base, sans passer par l'email de vérification."""
    from repositories.user_account_repository import UserAccountRepository

    db = db_module.SessionLocal()
    try:
        account = UserAccountRepository.get_by_email(db, email)
        UserAccountRepository.activate_user(db, account.id)
        db.commit()
    finally:
        db.close()


@pytest.fixture
def activate_account():
    return _activate_account


@pytest.fixture
def auth_headers(client):
    client.post("/auth/signup", json={
        "email": "client@bookurtrim.fr",
        "password": "motdepasse123",
        "role": "client",
        "first_name": "Marie",
        "last_name": "Dupont",
        "phone": "+33 6 12 34 56 78",
    })
    _activate_account("client@bookurtrim.fr")
    resp = client.post("/auth/login", json={
        "email": "client@bookurtrim.fr",
        "password": "motdepasse123",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def provider_auth_headers(client):
    client.post("/auth/signup", json={
        "email": "provider@bookurtrim.fr",
        "password": "motdepasse123",
        "role": "provider",
        "first_name": "Léa",
        "last_name": "Martin",
        "phone": "+33 6 98 76 54 32",
    })
    _activate_account("provider@bookurtrim.fr")
    resp = client.post("/auth/login", json={
        "email": "provider@bookurtrim.fr",
        "password": "motdepasse123",
    })
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# ── Profils (récupérés depuis /me car créés au signup) ────────────────────────

@pytest.fixture
def client_profile(client, auth_headers):
    return client.get("/clients/me", headers=auth_headers).json()


@pytest.fixture
def provider_profile(client, provider_auth_headers):
    return client.get("/providers/me", headers=provider_auth_headers).json()


# ── Autres ressources ─────────────────────────────────────────────────────────

@pytest.fixture
def service(client, provider_auth_headers, provider_profile):
    resp = client.post("/services", json={
        "name": "Coupe femme",
        "description": "Coupe + brushing",
        "default_duration": 60,
        "base_price": 45.00,
    }, headers=provider_auth_headers)
    return resp.json()


@pytest.fixture
def service_with_deposit(client, provider_auth_headers, provider_profile):
    resp = client.post("/services", json={
        "name": "Coupe + Brushing",
        "default_duration": 60,
        "base_price": 65.00,
        "deposit_amount": 10.00,
    }, headers=provider_auth_headers)
    return resp.json()


@pytest.fixture
def appointment_with_deposit(client, auth_headers, client_profile, provider_profile, service_with_deposit):
    resp = client.post("/appointments", json={
        "provider_id": provider_profile["id"],
        "service_id": service_with_deposit["id"],
        "start_at": "2025-12-01T10:00:00Z",
        "end_at": "2025-12-01T11:00:00Z",
    }, headers=auth_headers)
    return resp.json()


@pytest.fixture
def availability(client, provider_auth_headers, provider_profile):
    resp = client.post("/availabilities", json={
        "day_date": "2025-12-01",
        "start_time": "09:00:00",
        "end_time": "18:00:00",
        "slot_type": "work",
    }, headers=provider_auth_headers)
    return resp.json()


# ── Rendez-vous ───────────────────────────────────────────────────────────────

@pytest.fixture
def appointment(client, auth_headers, client_profile, provider_profile):
    resp = client.post("/appointments", json={
        "provider_id": provider_profile["id"],
        "start_at": "2025-12-01T10:00:00Z",
        "end_at": "2025-12-01T11:00:00Z",
        "specific_request": "Coupe courte",
    }, headers=auth_headers)
    return resp.json()


@pytest.fixture
def confirmed_appointment(client, provider_auth_headers, appointment):
    appt_id = appointment["id"]
    resp = client.patch(f"/appointments/{appt_id}",
                        json={"status": "confirmed"},
                        headers=provider_auth_headers)
    return resp.json()


@pytest.fixture
def completed_appointment(client, provider_auth_headers, confirmed_appointment):
    appt_id = confirmed_appointment["id"]
    resp = client.patch(f"/appointments/{appt_id}",
                        json={"status": "completed"},
                        headers=provider_auth_headers)
    return resp.json()
