import jwt

import config


def _make_verification_token(email: str, exp_delta_hours: int = 24, token_type: str = "verify_email") -> str:
    from datetime import datetime, timedelta, timezone

    return jwt.encode(
        {
            "sub": email,
            "type": token_type,
            "exp": datetime.now(timezone.utc) + timedelta(hours=exp_delta_hours),
        },
        config.JWT_SECRET_KEY,
        algorithm="HS256",
    )


class TestVerifyEmail:
    def test_verify_email_activates_account(self, client):
        client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "client",
            "first_name": "Marie",
            "last_name": "Dupont",
        })
        token = _make_verification_token("user@test.fr")

        resp = client.get(f"/auth/verify-email?token={token}")
        assert resp.status_code == 200

        login = client.post("/auth/login", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
        })
        assert login.status_code == 200
        assert "access_token" in login.json()

    def test_verify_email_already_active(self, client, activate_account):
        client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "client",
            "first_name": "Marie",
            "last_name": "Dupont",
        })
        activate_account("user@test.fr")
        token = _make_verification_token("user@test.fr")

        resp = client.get(f"/auth/verify-email?token={token}")
        assert resp.status_code == 200

    def test_verify_email_invalid_token(self, client):
        resp = client.get("/auth/verify-email?token=token-invalide")
        assert resp.status_code == 400

    def test_verify_email_wrong_token_type(self, client):
        client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "client",
            "first_name": "Marie",
            "last_name": "Dupont",
        })
        token = _make_verification_token("user@test.fr", token_type="access")

        resp = client.get(f"/auth/verify-email?token={token}")
        assert resp.status_code == 400

    def test_verify_email_unknown_account(self, client):
        token = _make_verification_token("inconnu@test.fr")
        resp = client.get(f"/auth/verify-email?token={token}")
        assert resp.status_code == 400


class TestSignup:
    def test_signup_success(self, client):
        resp = client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "client",
            "first_name": "Marie",
            "last_name": "Dupont",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "user@test.fr"
        assert data["role"] == "client"
        assert data["is_active"] is False
        assert "password_hash" not in data

    def test_signup_provider(self, client):
        resp = client.post("/auth/signup", json={
            "email": "provider@test.fr",
            "password": "motdepasse123",
            "role": "provider",
            "first_name": "Léa",
            "last_name": "Martin",
        })
        assert resp.status_code == 201
        assert resp.json()["role"] == "provider"

    def test_signup_duplicate_email(self, client):
        payload = {"email": "dup@test.fr", "password": "motdepasse123", "role": "client", "first_name": "Marie", "last_name": "Dupont"}
        client.post("/auth/signup", json=payload)
        resp = client.post("/auth/signup", json=payload)
        assert resp.status_code == 409

    def test_signup_invalid_email(self, client):
        resp = client.post("/auth/signup", json={
            "email": "pas-un-email",
            "password": "motdepasse123",
            "role": "client",
            "first_name": "Marie",
            "last_name": "Dupont",
        })
        assert resp.status_code == 422

    def test_signup_password_too_short(self, client):
        resp = client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "court",
            "role": "client",
            "first_name": "Marie",
            "last_name": "Dupont",
        })
        assert resp.status_code == 422

    def test_signup_invalid_role(self, client):
        resp = client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "admin",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client, activate_account):
        client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "client",
            "first_name": "Marie",
            "last_name": "Dupont",
        })
        activate_account("user@test.fr")
        resp = client.post("/auth/login", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "client"

    def test_login_unverified_account(self, client):
        client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "client",
            "first_name": "Marie",
            "last_name": "Dupont",
        })
        resp = client.post("/auth/login", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
        })
        assert resp.status_code == 403

    def test_login_wrong_password(self, client, activate_account):
        client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "client",
            "first_name": "Marie",
            "last_name": "Dupont",
        })
        activate_account("user@test.fr")
        resp = client.post("/auth/login", json={
            "email": "user@test.fr",
            "password": "mauvaismdp",
        })
        assert resp.status_code == 401

    def test_login_unknown_email(self, client):
        resp = client.post("/auth/login", json={
            "email": "inconnu@test.fr",
            "password": "motdepasse123",
        })
        assert resp.status_code == 401


    def test_signup_also_creates_client_profile(self, client, activate_account):
        client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "client",
            "first_name": "Marie",
            "last_name": "Dupont",
        })
        activate_account("user@test.fr")
        resp = client.post("/auth/login", json={"email": "user@test.fr", "password": "motdepasse123"})
        token = resp.json()["access_token"]
        me = client.get("/clients/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["first_name"] == "Marie"

    def test_signup_also_creates_provider_profile(self, client, activate_account):
        client.post("/auth/signup", json={
            "email": "provider@test.fr",
            "password": "motdepasse123",
            "role": "provider",
            "first_name": "Léa",
            "last_name": "Martin",
        })
        activate_account("provider@test.fr")
        resp = client.post("/auth/login", json={"email": "provider@test.fr", "password": "motdepasse123"})
        token = resp.json()["access_token"]
        me = client.get("/providers/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200
        assert me.json()["first_name"] == "Léa"
