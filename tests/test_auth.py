class TestSignup:
    def test_signup_success(self, client):
        resp = client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "client",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "user@test.fr"
        assert data["role"] == "client"
        assert data["is_active"] is True
        assert "password_hash" not in data

    def test_signup_provider(self, client):
        resp = client.post("/auth/signup", json={
            "email": "provider@test.fr",
            "password": "motdepasse123",
            "role": "provider",
        })
        assert resp.status_code == 201
        assert resp.json()["role"] == "provider"

    def test_signup_duplicate_email(self, client):
        payload = {"email": "dup@test.fr", "password": "motdepasse123", "role": "client"}
        client.post("/auth/signup", json=payload)
        resp = client.post("/auth/signup", json=payload)
        assert resp.status_code == 409

    def test_signup_invalid_email(self, client):
        resp = client.post("/auth/signup", json={
            "email": "pas-un-email",
            "password": "motdepasse123",
            "role": "client",
        })
        assert resp.status_code == 422

    def test_signup_password_too_short(self, client):
        resp = client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "court",
            "role": "client",
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
    def test_login_success(self, client):
        client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "client",
        })
        resp = client.post("/auth/login", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "client"

    def test_login_wrong_password(self, client):
        client.post("/auth/signup", json={
            "email": "user@test.fr",
            "password": "motdepasse123",
            "role": "client",
        })
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
