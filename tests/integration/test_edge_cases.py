"""
Tests d'intégration — Cas limites et scénarios manquants
"""
from unittest.mock import MagicMock, patch


class TestPagination:
    def _create_3_appointments(self, client, auth_headers, provider_auth_headers, provider_profile):
        """Crée 3 RDV en confirmant entre les créations pour contourner la limite de 2 PENDING."""
        ids = []
        for i in range(1, 4):
            r = client.post("/appointments", json={
                "provider_id": provider_profile["id"],
                "start_at": f"2025-12-0{i}T10:00:00Z",
                "end_at": f"2025-12-0{i}T11:00:00Z",
            }, headers=auth_headers)
            appt_id = r.json()["id"]
            ids.append(appt_id)
            # Confirmer pour libérer le slot PENDING avant le prochain
            client.patch(f"/appointments/{appt_id}",
                         json={"status": "confirmed"}, headers=provider_auth_headers)
        return ids

    def test_appointments_client_pagination(self, client, auth_headers, provider_auth_headers,
                                             client_profile, provider_profile):
        # Arrange — créer 3 RDV (confirmés pour éviter la limite PENDING)
        self._create_3_appointments(client, auth_headers, provider_auth_headers, provider_profile)

        # Act — page 1, limit 2
        resp = client.get("/appointments/client?page=1&limit=2", headers=auth_headers)

        # Assert
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["limit"] == 2

    def test_appointments_client_page2(self, client, auth_headers, provider_auth_headers,
                                        client_profile, provider_profile):
        # Arrange — créer 3 RDV confirmés
        self._create_3_appointments(client, auth_headers, provider_auth_headers, provider_profile)

        # Act — page 2, limit 2 → 1 résultat restant
        resp = client.get("/appointments/client?page=2&limit=2", headers=auth_headers)

        # Assert
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 1

    def test_providers_pagination(self, client, provider_profile):
        resp = client.get("/providers?page=1&limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["limit"] == 10

    def test_reviews_pagination_by_provider(self, client, provider_profile,
                                             auth_headers, provider_auth_headers,
                                             client_profile):
        # Arrange — créer un RDV, le compléter, laisser un avis
        appt = client.post("/appointments", json={
            "provider_id": provider_profile["id"],
            "start_at": "2025-12-01T10:00:00Z",
            "end_at": "2025-12-01T11:00:00Z",
        }, headers=auth_headers).json()

        client.patch(f"/appointments/{appt['id']}",
                     json={"status": "confirmed"}, headers=provider_auth_headers)
        client.patch(f"/appointments/{appt['id']}",
                     json={"status": "completed"}, headers=provider_auth_headers)

        client.post(f"/appointments/{appt['id']}/review", json={
            "appointment_id": appt["id"], "rating": 5,
        }, headers=auth_headers)

        # Act
        resp = client.get(f"/providers/{provider_profile['id']}/reviews?page=1&limit=20")

        # Assert
        assert resp.status_code == 200
        assert resp.json()["total"] == 1
        assert resp.json()["items"][0]["rating"] == 5


class TestAppointmentWithAnswers:
    def test_create_appointment_with_answers(self, client, auth_headers,
                                              client_profile, provider_profile):
        # Act
        resp = client.post("/appointments", json={
            "provider_id": provider_profile["id"],
            "start_at": "2025-12-01T10:00:00Z",
            "end_at": "2025-12-01T11:30:00Z",
            "answers": [
                {"question": "Type de cheveux", "answer": "Bouclé", "extra_minutes": 25},
                {"question": "Longueur", "answer": "Long", "extra_minutes": 20},
            ],
        }, headers=auth_headers)

        # Assert
        assert resp.status_code == 201
        data = resp.json()
        assert len(data["answers"]) == 2
        assert data["answers"][0]["question"] == "Type de cheveux"
        assert data["answers"][0]["extra_minutes"] == 25

    def test_answers_visible_in_get(self, client, auth_headers, appointment, client_profile):
        # Act
        resp = client.get(f"/appointments/{appointment['id']}", headers=auth_headers)

        # Assert
        assert resp.status_code == 200
        # answers peut être null si pas fourni à la création
        assert "answers" in resp.json()


class TestCancelByProviderWithRefund:
    def _prepare_confirmed_payment(self, client, auth_headers, provider_auth_headers,
                                    appointment, pi_id="pi_cancel", charge_id="ch_cancel"):
        """Crée et valide un paiement, puis confirme le RDV."""
        create = client.post("/payments", json={
            "appointment_id": appointment["id"],
            "amount": 20.00,
            "currency": "eur",
            "payment_type": "deposit",
        }, headers=auth_headers)
        pid = create.json()["id"]

        mock_intent = MagicMock()
        mock_intent.id = pi_id
        mock_intent.client_secret = "secret"
        with patch("stripe.PaymentIntent.create", return_value=mock_intent):
            client.post(f"/payments/{pid}/prepare", headers=auth_headers)

        webhook_headers = {"stripe-signature": "sig", "content-type": "application/json"}
        event = {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": pi_id, "latest_charge": charge_id, "metadata": {}}},
        }
        with patch("config.STRIPE_WEBHOOK_SECRET", "whsec_test"), \
             patch("stripe.Webhook.construct_event", return_value=event):
            client.post("/payments/webhook", content=b"payload", headers=webhook_headers)

        return pid

    def test_cancel_by_provider_refunds_validated_payment(
            self, client, auth_headers, provider_auth_headers, appointment):
        # Arrange
        pid = self._prepare_confirmed_payment(
            client, auth_headers, provider_auth_headers, appointment
        )

        # Act
        with patch("stripe.Refund.create"):
            resp = client.post(
                f"/appointments/{appointment['id']}/cancel-by-provider",
                headers=provider_auth_headers,
            )

        # Assert
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

        payment = client.get(f"/payments/{pid}", headers=auth_headers).json()
        assert payment["status"] == "refunded"

    def test_cancel_by_provider_no_refund_when_no_payment(
            self, client, provider_auth_headers, appointment):
        # Act — RDV PENDING sans paiement
        resp = client.post(
            f"/appointments/{appointment['id']}/cancel-by-provider",
            headers=provider_auth_headers,
        )

        # Assert — annulation OK, pas d'erreur Stripe
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"
