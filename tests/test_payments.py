from unittest.mock import MagicMock, patch


class TestPayments:
    def test_initiate_success(self, client, auth_headers, appointment):
        resp = client.post("/payments", json={
            "appointment_id": appointment["id"],
            "amount": 20.00,
            "currency": "eur",
            "payment_type": "deposit",
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert data["payment_type"] == "deposit"
        assert data["paid_at"] is None

    def test_initiate_unauthorized(self, client, appointment):
        resp = client.post("/payments", json={
            "appointment_id": appointment["id"],
            "amount": 20.00,
            "payment_type": "deposit",
        })
        assert resp.status_code == 401

    def test_initiate_appointment_not_found(self, client, auth_headers, client_profile):
        resp = client.post("/payments", json={
            "appointment_id": 9999,
            "amount": 20.00,
            "payment_type": "deposit",
        }, headers=auth_headers)
        assert resp.status_code == 404

    def test_deposit_already_paid(self, client, auth_headers, appointment):
        payload = {
            "appointment_id": appointment["id"],
            "amount": 20.00,
            "payment_type": "deposit",
        }
        client.post("/payments", json=payload, headers=auth_headers)
        resp = client.post("/payments", json=payload, headers=auth_headers)
        assert resp.status_code == 409

    def test_balance_after_deposit(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        client.post("/payments", json={
            "appointment_id": appt_id, "amount": 20.00, "payment_type": "deposit",
        }, headers=auth_headers)
        resp = client.post("/payments", json={
            "appointment_id": appt_id, "amount": 25.00, "payment_type": "balance",
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["payment_type"] == "balance"

    def test_get_payment_success(self, client, auth_headers, appointment):
        create = client.post("/payments", json={
            "appointment_id": appointment["id"],
            "amount": 20.00,
            "payment_type": "deposit",
        }, headers=auth_headers)
        pid = create.json()["id"]
        resp = client.get(f"/payments/{pid}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == pid

    def test_get_payment_not_found(self, client, auth_headers, client_profile):
        resp = client.get("/payments/9999", headers=auth_headers)
        assert resp.status_code == 404

    def test_list_by_appointment(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        client.post("/payments", json={
            "appointment_id": appt_id, "amount": 20.00, "payment_type": "deposit",
        }, headers=auth_headers)
        client.post("/payments", json={
            "appointment_id": appt_id, "amount": 25.00, "payment_type": "balance",
        }, headers=auth_headers)

        resp = client.get(f"/payments/appointment/{appt_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_invalid_amount(self, client, auth_headers, appointment):
        resp = client.post("/payments", json={
            "appointment_id": appointment["id"],
            "amount": -10.00,
            "payment_type": "deposit",
        }, headers=auth_headers)
        assert resp.status_code == 422

    # ── /prepare ──────────────────────────────────────────────────────────────

    def test_prepare_success(self, client, auth_headers, appointment):
        create = client.post("/payments", json={
            "appointment_id": appointment["id"],
            "amount": 20.00,
            "payment_type": "deposit",
        }, headers=auth_headers)
        pid = create.json()["id"]

        mock_intent = MagicMock()
        mock_intent.id = "pi_test_123"
        mock_intent.client_secret = "pi_test_123_secret_abc"

        with patch("stripe.PaymentIntent.create", return_value=mock_intent):
            resp = client.post(f"/payments/{pid}/prepare", headers=auth_headers)

        assert resp.status_code == 200
        data = resp.json()
        assert data["payment_id"] == pid
        assert data["client_secret"] == "pi_test_123_secret_abc"

    def test_prepare_idempotent(self, client, auth_headers, appointment):
        create = client.post("/payments", json={
            "appointment_id": appointment["id"],
            "amount": 20.00,
            "payment_type": "deposit",
        }, headers=auth_headers)
        pid = create.json()["id"]

        mock_intent = MagicMock()
        mock_intent.id = "pi_test_456"
        mock_intent.client_secret = "pi_test_456_secret_xyz"

        with patch("stripe.PaymentIntent.create", return_value=mock_intent):
            client.post(f"/payments/{pid}/prepare", headers=auth_headers)

        with patch("stripe.PaymentIntent.retrieve", return_value=mock_intent):
            resp = client.post(f"/payments/{pid}/prepare", headers=auth_headers)

        assert resp.status_code == 200
        assert resp.json()["client_secret"] == "pi_test_456_secret_xyz"

    def test_prepare_payment_not_found(self, client, auth_headers):
        mock_intent = MagicMock()
        with patch("stripe.PaymentIntent.create", return_value=mock_intent):
            resp = client.post("/payments/9999/prepare", headers=auth_headers)
        assert resp.status_code == 404

    def test_prepare_unauthorized(self, client, appointment):
        resp = client.post("/payments/1/prepare")
        assert resp.status_code == 401

    # ── /webhook ──────────────────────────────────────────────────────────────

    WEBHOOK_HEADERS = {"stripe-signature": "sig", "content-type": "application/json"}

    def _post_webhook(self, client, event: dict):
        with patch("config.STRIPE_WEBHOOK_SECRET", "whsec_test"), \
             patch("stripe.Webhook.construct_event", return_value=event):
            return client.post("/payments/webhook", content=b"payload", headers=self.WEBHOOK_HEADERS)

    def _prepare_payment(self, client, auth_headers, appointment, pi_id: str) -> int:
        create = client.post("/payments", json={
            "appointment_id": appointment["id"],
            "amount": 20.00,
            "payment_type": "deposit",
        }, headers=auth_headers)
        pid = create.json()["id"]
        mock_intent = MagicMock()
        mock_intent.id = pi_id
        mock_intent.client_secret = "secret"
        with patch("stripe.PaymentIntent.create", return_value=mock_intent):
            client.post(f"/payments/{pid}/prepare", headers=auth_headers)
        return pid

    def test_webhook_invalid_signature(self, client):
        import stripe
        with patch("config.STRIPE_WEBHOOK_SECRET", "whsec_test"), \
             patch("stripe.Webhook.construct_event", side_effect=stripe.SignatureVerificationError("bad", "sig")):
            resp = client.post("/payments/webhook", content=b"payload", headers=self.WEBHOOK_HEADERS)
        assert resp.status_code == 400

    def test_webhook_no_secret_configured(self, client):
        with patch("config.STRIPE_WEBHOOK_SECRET", ""):
            resp = client.post("/payments/webhook", content=b"payload", headers=self.WEBHOOK_HEADERS)
        assert resp.status_code == 500

    def test_webhook_payment_succeeded(self, client, auth_headers, appointment):
        pid = self._prepare_payment(client, auth_headers, appointment, "pi_succeeded")
        event = {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_succeeded", "latest_charge": "ch_001", "metadata": {}}},
        }
        resp = self._post_webhook(client, event)
        assert resp.status_code == 200
        assert client.get(f"/payments/{pid}", headers=auth_headers).json()["status"] == "validated"

    def test_webhook_payment_failed(self, client, auth_headers, appointment):
        pid = self._prepare_payment(client, auth_headers, appointment, "pi_failed")
        event = {
            "type": "payment_intent.payment_failed",
            "data": {"object": {"id": "pi_failed"}},
        }
        resp = self._post_webhook(client, event)
        assert resp.status_code == 200
        assert client.get(f"/payments/{pid}", headers=auth_headers).json()["status"] == "failed"

    def test_webhook_charge_refunded(self, client, auth_headers, appointment):
        pid = self._prepare_payment(client, auth_headers, appointment, "pi_refund")
        succeed_event = {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_refund", "latest_charge": "ch_refund", "metadata": {}}},
        }
        self._post_webhook(client, succeed_event)

        refund_event = {
            "type": "charge.refunded",
            "data": {"object": {"id": "ch_refund"}},
        }
        resp = self._post_webhook(client, refund_event)
        assert resp.status_code == 200
        assert client.get(f"/payments/{pid}", headers=auth_headers).json()["status"] == "refunded"
