"""
Tests d'intégration — Reçus (receipts)
"""
from unittest.mock import MagicMock, patch


def _confirm_payment(client, auth_headers, appointment_id, amount,
                     payment_type, pi_id, charge_id):
    """Helper : crée, prépare et confirme un paiement via webhook."""
    create = client.post("/payments", json={
        "appointment_id": appointment_id,
        "amount": amount,
        "currency": "eur",
        "payment_type": payment_type,
    }, headers=auth_headers)
    pid = create.json()["id"]

    mock_intent = MagicMock()
    mock_intent.id = pi_id
    mock_intent.client_secret = "secret"
    with patch("stripe.PaymentIntent.create", return_value=mock_intent):
        client.post(f"/payments/{pid}/prepare", headers=auth_headers)

    mock_charge = MagicMock()
    mock_charge.receipt_url = f"https://pay.stripe.com/receipts/{charge_id}"
    event = {
        "type": "payment_intent.succeeded",
        "data": {"object": {"id": pi_id, "latest_charge": charge_id, "metadata": {}}},
    }
    with patch("config.STRIPE_WEBHOOK_SECRET", "whsec_test"), \
         patch("stripe.Webhook.construct_event", return_value=event), \
         patch("stripe.Charge.retrieve", return_value=mock_charge):
        client.post("/payments/webhook", content=b"payload",
                    headers={"stripe-signature": "sig", "content-type": "application/json"})
    return pid


class TestReceipts:
    def test_no_receipts_before_payment(self, client, auth_headers, appointment):
        resp = client.get(f"/appointments/{appointment['id']}/receipts",
                          headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_receipt_created_after_deposit_confirmed(self, client, auth_headers,
                                                       appointment_with_deposit):
        appt_id = appointment_with_deposit["id"]
        _confirm_payment(client, auth_headers, appt_id, 10.00, "deposit",
                         "pi_rcpt_dep", "ch_rcpt_dep")

        resp = client.get(f"/appointments/{appt_id}/receipts", headers=auth_headers)
        assert resp.status_code == 200
        receipts = resp.json()
        assert len(receipts) == 1
        assert receipts[0]["payment_type"] == "deposit"
        assert float(receipts[0]["amount"]) == 10.00
        assert receipts[0]["stripe_receipt_url"] == "https://pay.stripe.com/receipts/ch_rcpt_dep"

    def test_two_receipts_after_deposit_and_balance(self, client, auth_headers,
                                                      provider_auth_headers,
                                                      appointment_with_deposit):
        appt_id = appointment_with_deposit["id"]

        # Payer l'acompte
        _confirm_payment(client, auth_headers, appt_id, 10.00, "deposit",
                         "pi_dep_2", "ch_dep_2")

        # Compléter le RDV puis payer le solde
        client.post(f"/appointments/{appt_id}/complete", headers=provider_auth_headers)
        _confirm_payment(client, auth_headers, appt_id, 55.00, "balance",
                         "pi_bal_2", "ch_bal_2")

        resp = client.get(f"/appointments/{appt_id}/receipts", headers=auth_headers)
        assert resp.status_code == 200
        receipts = resp.json()
        assert len(receipts) == 2

        types = [r["payment_type"] for r in receipts]
        assert "deposit" in types
        assert "balance" in types

        amounts = {r["payment_type"]: float(r["amount"]) for r in receipts}
        assert amounts["deposit"] == 10.00
        assert amounts["balance"] == 55.00

    def test_receipts_unauthorized(self, client, appointment):
        resp = client.get(f"/appointments/{appointment['id']}/receipts")
        assert resp.status_code == 401

    def test_receipts_not_found(self, client, auth_headers, client_profile):
        resp = client.get("/appointments/9999/receipts", headers=auth_headers)
        assert resp.status_code == 404

    def test_no_receipt_for_cash_payment(self, client, auth_headers,
                                          provider_auth_headers, appointment_with_deposit):
        # Acompte payé en ligne
        appt_id = appointment_with_deposit["id"]
        _confirm_payment(client, auth_headers, appt_id, 10.00, "deposit",
                         "pi_cash", "ch_cash")

        # Solde payé en vrai vie → rien à appeler
        client.post(f"/appointments/{appt_id}/complete", headers=provider_auth_headers)

        # Seulement 1 reçu (acompte)
        resp = client.get(f"/appointments/{appt_id}/receipts", headers=auth_headers)
        assert len(resp.json()) == 1
        assert resp.json()[0]["payment_type"] == "deposit"
