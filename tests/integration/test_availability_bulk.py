"""
Tests d'intégration — Créneaux en masse + liaison RDV/service
"""

BULK_PAYLOAD = [
    {"day_date": "2026-06-09", "start_time": "09:00:00", "end_time": "18:00:00", "slot_type": "work"},
    {"day_date": "2026-06-10", "start_time": "09:00:00", "end_time": "18:00:00", "slot_type": "work"},
    {"day_date": "2026-06-11", "start_time": "09:00:00", "end_time": "18:00:00", "slot_type": "break"},
]


class TestBulkAvailabilities:
    def test_bulk_create_success(self, client, provider_auth_headers, provider_profile):
        # Act
        resp = client.post("/availabilities/bulk", json=BULK_PAYLOAD, headers=provider_auth_headers)

        # Assert
        assert resp.status_code == 201
        data = resp.json()
        assert len(data) == 3
        assert data[0]["slot_type"] == "work"
        assert data[2]["slot_type"] == "break"

    def test_bulk_create_unauthorized(self, client):
        resp = client.post("/availabilities/bulk", json=BULK_PAYLOAD)
        assert resp.status_code == 401

    def test_bulk_create_no_provider_profile(self, client, auth_headers):
        resp = client.post("/availabilities/bulk", json=BULK_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 404

    def test_bulk_create_visible_in_provider_availabilities(self, client, provider_auth_headers, provider_profile):
        # Arrange
        client.post("/availabilities/bulk", json=BULK_PAYLOAD, headers=provider_auth_headers)

        # Act
        resp = client.get(f"/providers/{provider_profile['id']}/availabilities")

        # Assert
        assert resp.status_code == 200
        assert len(resp.json()) == 3

    def test_bulk_create_with_date_filter(self, client, provider_auth_headers, provider_profile):
        # Arrange
        client.post("/availabilities/bulk", json=BULK_PAYLOAD, headers=provider_auth_headers)

        # Act
        resp = client.get(
            f"/providers/{provider_profile['id']}/availabilities?date=2026-06-09"
        )

        # Assert
        assert len(resp.json()) == 1
        assert resp.json()[0]["day_date"] == "2026-06-09"


class TestAppointmentWithService:
    def test_create_appointment_with_service_id(self, client, auth_headers, provider_auth_headers,
                                                 client_profile, provider_profile, service):
        # Act — RDV avec service_id
        resp = client.post("/appointments", json={
            "provider_id": provider_profile["id"],
            "service_id": service["id"],
            "start_at": "2025-12-01T10:00:00Z",
            "end_at": "2025-12-01T11:00:00Z",
        }, headers=auth_headers)

        # Assert
        assert resp.status_code == 201
        assert resp.json()["service_name"] == service["name"]

    def test_appointment_list_includes_service_name(self, client, auth_headers, provider_auth_headers,
                                                     client_profile, provider_profile, service):
        # Arrange
        client.post("/appointments", json={
            "provider_id": provider_profile["id"],
            "service_id": service["id"],
            "start_at": "2025-12-01T10:00:00Z",
            "end_at": "2025-12-01T11:00:00Z",
        }, headers=auth_headers)

        # Act
        resp = client.get("/appointments/client", headers=auth_headers)

        # Assert
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert items[0]["service_name"] == service["name"]

    def test_appointment_without_service_has_null_service_name(self, client, auth_headers,
                                                                 client_profile, provider_profile):
        # Act
        resp = client.post("/appointments", json={
            "provider_id": provider_profile["id"],
            "start_at": "2025-12-01T10:00:00Z",
            "end_at": "2025-12-01T11:00:00Z",
        }, headers=auth_headers)

        # Assert
        assert resp.status_code == 201
        assert resp.json()["service_name"] is None


class TestProviderBusinessProfile:
    def test_create_provider_with_business_info(self, client, provider_auth_headers, provider_profile):
        # Act
        resp = client.patch("/providers/me", json={
            "business_name": "Salon Dupont",
            "address": "12 rue de la Paix, 75001 Paris",
        }, headers=provider_auth_headers)

        # Assert
        assert resp.status_code == 200
        data = resp.json()
        assert data["business_name"] == "Salon Dupont"
        assert data["address"] == "12 rue de la Paix, 75001 Paris"

    def test_business_info_visible_in_public_profile(self, client, provider_auth_headers, provider_profile):
        # Arrange
        client.patch("/providers/me", json={
            "business_name": "Salon Public",
            "address": "5 avenue Test",
        }, headers=provider_auth_headers)

        # Act — accès public
        resp = client.get(f"/providers/{provider_profile['id']}")

        # Assert
        assert resp.status_code == 200
        assert resp.json()["business_name"] == "Salon Public"

    def test_business_info_null_by_default(self, client, provider_auth_headers, provider_profile):
        resp = client.get("/providers/me", headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["business_name"] is None
        assert resp.json()["address"] is None
