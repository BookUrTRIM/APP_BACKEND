"""
Tests d'intégration — Remboursement manuel (force majeure)
POST /payments/appointment/:id/refund
"""
from unittest.mock import MagicMock, patch


def _prepare_and_confirm_payment(client, auth_headers, appointment, pi_id="pi_test", charge_id="ch_test"):
    """Helper : crée un paiement, prépare le PaymentIntent et le confirme via webhook."""
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


class TestManualRefund:
    def test_refund_success(self, client, auth_headers, provider_auth_headers, appointment):
        # Arrange — paiement validé
        _prepare_and_confirm_payment(client, auth_headers, appointment)

        # Act
        with patch("stripe.Refund.create"):
            resp = client.post(
                f"/payments/appointment/{appointment['id']}/refund",
                headers=provider_auth_headers,
            )

        # Assert
        assert resp.status_code == 200
        assert resp.json()["status"] == "refunded"

    def test_refund_cancels_appointment(self, client, auth_headers, provider_auth_headers, appointment):
        # Arrange
        _prepare_and_confirm_payment(client, auth_headers, appointment)

        # Act
        with patch("stripe.Refund.create"):
            client.post(
                f"/payments/appointment/{appointment['id']}/refund",
                headers=provider_auth_headers,
            )

        # Assert — le RDV doit être annulé
        appt = client.get(f"/appointments/{appointment['id']}", headers=auth_headers).json()
        assert appt["status"] == "cancelled"

    def test_refund_422_when_no_validated_payment(self, client, auth_headers, provider_auth_headers, appointment):
        # Act — pas de paiement validé
        resp = client.post(
            f"/payments/appointment/{appointment['id']}/refund",
            headers=provider_auth_headers,
        )

        # Assert
        assert resp.status_code == 422

    def test_refund_unauthorized(self, client, appointment):
        resp = client.post(f"/payments/appointment/{appointment['id']}/refund")
        assert resp.status_code == 401

    def test_refund_stripe_error_returns_500(self, client, auth_headers, provider_auth_headers, appointment):
        # Arrange
        import stripe
        _prepare_and_confirm_payment(client, auth_headers, appointment)

        # Act
        with patch("stripe.Refund.create", side_effect=stripe.StripeError("Network error")):
            resp = client.post(
                f"/payments/appointment/{appointment['id']}/refund",
                headers=provider_auth_headers,
            )

        # Assert
        assert resp.status_code == 500
