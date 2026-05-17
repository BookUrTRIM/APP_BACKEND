class TestClientProfile:
    def test_signup_creates_profile(self, client, auth_headers):
        resp = client.get("/clients/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["first_name"] == "Marie"
        assert data["last_name"] == "Dupont"

    def test_create_client_unauthorized(self, client):
        resp = client.post("/clients", json={"first_name": "X", "last_name": "Y"})
        assert resp.status_code == 401

    def test_create_client_duplicate(self, client, auth_headers):
        resp = client.post("/clients", json={"first_name": "X", "last_name": "Y"}, headers=auth_headers)
        assert resp.status_code == 409

    def test_get_me_success(self, client, auth_headers):
        resp = client.get("/clients/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["last_name"] == "Dupont"

    def test_show_client(self, client, auth_headers, client_profile):
        resp = client.get(f"/clients/{client_profile['id']}", headers=auth_headers)
        assert resp.status_code == 200

    def test_update_client_success(self, client, auth_headers, client_profile):
        client_id = client_profile["id"]
        resp = client.patch(f"/clients/{client_id}", json={"hair_length": "Court"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["hair_length"] == "Court"

    def test_update_client_forbidden(self, client, auth_headers, provider_auth_headers, client_profile):
        client_id = client_profile["id"]
        resp = client.patch(f"/clients/{client_id}", json={"hair_length": "Court"}, headers=provider_auth_headers)
        assert resp.status_code == 403
