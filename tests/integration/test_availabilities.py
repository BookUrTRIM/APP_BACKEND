AVAIL_PAYLOAD = {
    "day_date": "2025-12-01",
    "start_time": "09:00:00",
    "end_time": "18:00:00",
    "slot_type": "work",
}


class TestAvailabilities:
    def test_create_success(self, client, provider_auth_headers, provider_profile):
        resp = client.post("/availabilities", json=AVAIL_PAYLOAD, headers=provider_auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["day_date"] == "2025-12-01"
        assert data["slot_type"] == "work"

    def test_create_unauthorized(self, client):
        resp = client.post("/availabilities", json=AVAIL_PAYLOAD)
        assert resp.status_code == 401

    def test_create_no_provider_profile(self, client, auth_headers):
        resp = client.post("/availabilities", json=AVAIL_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 404

    def test_create_invalid_times(self, client, provider_auth_headers, provider_profile):
        resp = client.post("/availabilities", json={
            **AVAIL_PAYLOAD,
            "start_time": "18:00:00",
            "end_time": "09:00:00",
        }, headers=provider_auth_headers)
        assert resp.status_code == 422

    def test_create_break_slot(self, client, provider_auth_headers, provider_profile):
        resp = client.post("/availabilities", json={
            **AVAIL_PAYLOAD,
            "slot_type": "break",
        }, headers=provider_auth_headers)
        assert resp.status_code == 201
        assert resp.json()["slot_type"] == "break"

    def test_update_success(self, client, provider_auth_headers, availability):
        aid = availability["id"]
        resp = client.patch(f"/availabilities/{aid}",
                            json={"end_time": "20:00:00"},
                            headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["end_time"] == "20:00:00"

    def test_update_unauthorized(self, client, availability):
        resp = client.patch(f"/availabilities/{availability['id']}", json={"end_time": "20:00:00"})
        assert resp.status_code == 401

    def test_update_forbidden(self, client, auth_headers, availability):
        resp = client.patch(f"/availabilities/{availability['id']}",
                            json={"end_time": "20:00:00"},
                            headers=auth_headers)
        assert resp.status_code == 403

    def test_update_not_found(self, client, provider_auth_headers, provider_profile):
        resp = client.patch("/availabilities/9999", json={"end_time": "20:00:00"}, headers=provider_auth_headers)
        assert resp.status_code == 404

    def test_delete_success(self, client, provider_auth_headers, availability):
        aid = availability["id"]
        assert client.delete(f"/availabilities/{aid}", headers=provider_auth_headers).status_code == 204

    def test_delete_unauthorized(self, client, availability):
        resp = client.delete(f"/availabilities/{availability['id']}")
        assert resp.status_code == 401

    def test_delete_forbidden(self, client, auth_headers, availability):
        resp = client.delete(f"/availabilities/{availability['id']}", headers=auth_headers)
        assert resp.status_code == 403

    def test_delete_not_found(self, client, provider_auth_headers, provider_profile):
        resp = client.delete("/availabilities/9999", headers=provider_auth_headers)
        assert resp.status_code == 404
