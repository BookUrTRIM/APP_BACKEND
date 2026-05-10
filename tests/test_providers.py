PROVIDER_PAYLOAD = {
    "last_name": "Martin",
    "first_name": "Léa",
    "phone": "+33 6 98 76 54 32",
}

SERVICE_PAYLOAD = {
    "name": "Coupe femme",
    "description": "Coupe + brushing",
    "default_duration": 60,
    "base_price": 45.00,
}


class TestProviderProfile:
    def test_create_provider_success(self, client, provider_auth_headers):
        resp = client.post("/providers", json=PROVIDER_PAYLOAD, headers=provider_auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["last_name"] == "Martin"
        assert "google_calendar_token_enc" not in data

    def test_create_provider_unauthorized(self, client):
        resp = client.post("/providers", json=PROVIDER_PAYLOAD)
        assert resp.status_code == 401

    def test_create_provider_duplicate(self, client, provider_auth_headers):
        client.post("/providers", json=PROVIDER_PAYLOAD, headers=provider_auth_headers)
        resp = client.post("/providers", json=PROVIDER_PAYLOAD, headers=provider_auth_headers)
        assert resp.status_code == 409

    def test_list_providers_public(self, client, provider_profile):
        resp = client.get("/providers")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["page"] == 1

    def test_list_providers_empty(self, client):
        resp = client.get("/providers")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_show_provider(self, client, provider_profile):
        pid = provider_profile["id"]
        resp = client.get(f"/providers/{pid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == pid

    def test_show_provider_not_found(self, client):
        resp = client.get("/providers/9999")
        assert resp.status_code == 404

    def test_get_me(self, client, provider_auth_headers, provider_profile):
        resp = client.get("/providers/me", headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["first_name"] == "Léa"

    def test_get_me_no_profile(self, client, provider_auth_headers):
        resp = client.get("/providers/me", headers=provider_auth_headers)
        assert resp.status_code == 404

    def test_update_provider(self, client, provider_auth_headers, provider_profile):
        pid = provider_profile["id"]
        resp = client.patch(f"/providers/{pid}", json={"phone": "+33 1 23 45 67 89"}, headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["phone"] == "+33 1 23 45 67 89"

    def test_update_provider_forbidden(self, client, auth_headers, provider_profile):
        pid = provider_profile["id"]
        resp = client.patch(f"/providers/{pid}", json={"phone": "000"}, headers=auth_headers)
        assert resp.status_code == 403

    def test_list_services_by_provider(self, client, provider_profile, service):
        pid = provider_profile["id"]
        resp = client.get(f"/providers/{pid}/services")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_list_availabilities_by_provider(self, client, provider_profile, availability):
        pid = provider_profile["id"]
        resp = client.get(f"/providers/{pid}/availabilities")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_list_availabilities_with_date_filter(self, client, provider_profile, availability):
        pid = provider_profile["id"]
        resp = client.get(f"/providers/{pid}/availabilities?date=2025-12-01")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

        resp_wrong = client.get(f"/providers/{pid}/availabilities?date=2025-06-01")
        assert resp_wrong.status_code == 200
        assert len(resp_wrong.json()) == 0

    def test_list_reviews_by_provider(self, client, provider_profile):
        pid = provider_profile["id"]
        resp = client.get(f"/providers/{pid}/reviews")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestServices:
    def test_create_service_success(self, client, provider_auth_headers, provider_profile):
        resp = client.post("/services", json=SERVICE_PAYLOAD, headers=provider_auth_headers)
        assert resp.status_code == 201
        assert resp.json()["name"] == "Coupe femme"
        assert resp.json()["default_duration"] == 60

    def test_create_service_unauthorized(self, client):
        resp = client.post("/services", json=SERVICE_PAYLOAD)
        assert resp.status_code == 401

    def test_create_service_no_provider_profile(self, client, auth_headers):
        resp = client.post("/services", json=SERVICE_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 404

    def test_get_service(self, client, service):
        sid = service["id"]
        resp = client.get(f"/services/{sid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == sid

    def test_get_service_not_found(self, client):
        resp = client.get("/services/9999")
        assert resp.status_code == 404

    def test_update_service(self, client, provider_auth_headers, service):
        sid = service["id"]
        resp = client.patch(f"/services/{sid}", json={"base_price": 55.00}, headers=provider_auth_headers)
        assert resp.status_code == 200
        assert float(resp.json()["base_price"]) == 55.0

    def test_update_service_forbidden(self, client, auth_headers, service):
        sid = service["id"]
        resp = client.patch(f"/services/{sid}", json={"name": "Hack"}, headers=auth_headers)
        assert resp.status_code == 403

    def test_delete_service(self, client, provider_auth_headers, service):
        sid = service["id"]
        assert client.delete(f"/services/{sid}", headers=provider_auth_headers).status_code == 204
        assert client.get(f"/services/{sid}").status_code == 404

    def test_delete_service_forbidden(self, client, auth_headers, service):
        sid = service["id"]
        resp = client.delete(f"/services/{sid}", headers=auth_headers)
        assert resp.status_code == 403
