"""
Tests d'intégration — Règles métier avancées sur les rendez-vous
"""


class TestPendingLimit:
    def test_should_block_third_pending_appointment(self, client, auth_headers, client_profile, provider_profile):
        # Arrange — créer 2 RDV PENDING
        payload = {
            "provider_id": provider_profile["id"],
            "start_at": "2025-12-01T10:00:00Z",
            "end_at": "2025-12-01T11:00:00Z",
        }
        client.post("/appointments", json=payload, headers=auth_headers)
        client.post("/appointments", json={
            **payload,
            "start_at": "2025-12-02T10:00:00Z",
            "end_at": "2025-12-02T11:00:00Z",
        }, headers=auth_headers)

        # Act — 3ème RDV doit être refusé
        resp = client.post("/appointments", json={
            **payload,
            "start_at": "2025-12-03T10:00:00Z",
            "end_at": "2025-12-03T11:00:00Z",
        }, headers=auth_headers)

        # Assert
        assert resp.status_code == 422
        assert "2" in resp.json()["error"]

    def test_should_allow_after_cancel(self, client, auth_headers, client_profile, provider_profile):
        # Arrange — 2 RDV PENDING
        payload = {
            "provider_id": provider_profile["id"],
            "start_at": "2025-12-01T10:00:00Z",
            "end_at": "2025-12-01T11:00:00Z",
        }
        r1 = client.post("/appointments", json=payload, headers=auth_headers).json()
        client.post("/appointments", json={
            **payload,
            "start_at": "2025-12-02T10:00:00Z",
            "end_at": "2025-12-02T11:00:00Z",
        }, headers=auth_headers)

        # Annuler le premier
        client.post(f"/appointments/{r1['id']}/cancel", headers=auth_headers)

        # Act — 3ème RDV autorisé car 1 annulé
        resp = client.post("/appointments", json={
            **payload,
            "start_at": "2025-12-03T10:00:00Z",
            "end_at": "2025-12-03T11:00:00Z",
        }, headers=auth_headers)

        # Assert
        assert resp.status_code == 201


class TestCancelEndpoints:
    def test_cancel_by_client_success(self, client, auth_headers, appointment):
        # Act
        resp = client.post(f"/appointments/{appointment['id']}/cancel-by-client",
                           headers=auth_headers)

        # Assert
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_cancel_by_client_forbidden_for_provider(self, client, provider_auth_headers, appointment):
        resp = client.post(f"/appointments/{appointment['id']}/cancel-by-client",
                           headers=provider_auth_headers)
        assert resp.status_code == 403

    def test_cancel_by_provider_success(self, client, provider_auth_headers, appointment):
        resp = client.post(f"/appointments/{appointment['id']}/cancel-by-provider",
                           headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_cancel_by_provider_forbidden_for_client(self, client, auth_headers, appointment):
        resp = client.post(f"/appointments/{appointment['id']}/cancel-by-provider",
                           headers=auth_headers)
        assert resp.status_code == 403


class TestCompleteEndpoint:
    def test_complete_success_by_provider(self, client, provider_auth_headers, confirmed_appointment):
        # Act
        resp = client.post(
            f"/appointments/{confirmed_appointment['id']}/complete",
            headers=provider_auth_headers,
        )

        # Assert
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_complete_forbidden_for_client(self, client, auth_headers, confirmed_appointment):
        resp = client.post(
            f"/appointments/{confirmed_appointment['id']}/complete",
            headers=auth_headers,
        )
        assert resp.status_code == 403

    def test_complete_invalid_transition_from_pending(self, client, provider_auth_headers, appointment):
        resp = client.post(
            f"/appointments/{appointment['id']}/complete",
            headers=provider_auth_headers,
        )
        assert resp.status_code == 400

    def test_complete_auto_generates_invoice(self, client, provider_auth_headers, confirmed_appointment):
        # Act
        appt_id = confirmed_appointment["id"]
        client.post(f"/appointments/{appt_id}/complete", headers=provider_auth_headers)

        # Assert — la facture est générée automatiquement
        resp = client.get(f"/appointments/{appt_id}/invoice", headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["appointment_id"] == appt_id
