CLIENT_PAYLOAD = {
    "last_name": "Dupont",
    "first_name": "Marie",
    "phone": "+33 6 12 34 56 78",
    "hair_type": "Bouclé",
    "hair_length": "Long",
}


class TestClientProfile:
    def test_create_client_success(self, client, auth_headers):
        resp = client.post("/clients", json=CLIENT_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["last_name"] == "Dupont"
        assert data["first_name"] == "Marie"

    def test_create_client_unauthorized(self, client):
        resp = client.post("/clients", json=CLIENT_PAYLOAD)
        assert resp.status_code == 401

    def test_create_client_duplicate(self, client, auth_headers):
        client.post("/clients", json=CLIENT_PAYLOAD, headers=auth_headers)
        resp = client.post("/clients", json=CLIENT_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 409

    def test_get_me_success(self, client, auth_headers):
        client.post("/clients", json=CLIENT_PAYLOAD, headers=auth_headers)
        resp = client.get("/clients/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["last_name"] == "Dupont"

    def test_get_me_no_profile(self, client, auth_headers):
        resp = client.get("/clients/me", headers=auth_headers)
        assert resp.status_code == 404

    def test_update_client_success(self, client, auth_headers):
        create = client.post("/clients", json=CLIENT_PAYLOAD, headers=auth_headers)
        client_id = create.json()["id"]

        resp = client.patch(f"/clients/{client_id}", json={"hair_length": "Court"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["hair_length"] == "Court"

    def test_update_client_forbidden(self, client, auth_headers, provider_auth_headers):
        create = client.post("/clients", json=CLIENT_PAYLOAD, headers=auth_headers)
        client_id = create.json()["id"]

        resp = client.patch(f"/clients/{client_id}", json={"hair_length": "Court"}, headers=provider_auth_headers)
        assert resp.status_code == 403
