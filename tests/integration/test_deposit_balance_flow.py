"""
Tests d'intégration — Flux acompte + solde
"""
from unittest.mock import MagicMock, patch


def _prepare_and_confirm(client, auth_headers, appointment_id, pi_id, charge_id):
    """Helper : initie, prépare et confirme un paiement deposit via webhook."""
    create = client.post("/payments", json={
        "appointment_id": appointment_id,
        "amount": 10.00,
        "currency": "eur",
        "payment_type": "deposit",
    }, headers=auth_headers)
    pid = create.json()["id"]

    mock_intent = MagicMock()
    mock_intent.id = pi_id
    mock_intent.client_secret = "secret"
    with patch("stripe.PaymentIntent.create", return_value=mock_intent):
        client.post(f"/payments/{pid}/prepare", headers=auth_headers)

    event = {
        "type": "payment_intent.succeeded",
        "data": {"object": {"id": pi_id, "latest_charge": charge_id, "metadata": {}}},
    }
    mock_charge = MagicMock()
    mock_charge.receipt_url = "https://pay.stripe.com/receipts/test"
    with patch("config.STRIPE_WEBHOOK_SECRET", "whsec_test"), \
         patch("stripe.Webhook.construct_event", return_value=event), \
         patch("stripe.Charge.retrieve", return_value=mock_charge):
        client.post("/payments/webhook", content=b"payload",
                    headers={"stripe-signature": "sig", "content-type": "application/json"})
    return pid


class TestServiceWithDeposit:
    def test_service_has_deposit_amount(self, client, service_with_deposit):
        assert float(service_with_deposit["base_price"]) == 65.00
        assert float(service_with_deposit["deposit_amount"]) == 10.00

    def test_service_without_deposit_has_null(self, client, service):
        assert service["deposit_amount"] is None

    def test_update_service_deposit_amount(self, client, provider_auth_headers, service):
        resp = client.patch(f"/services/{service['id']}",
                            json={"deposit_amount": 15.00},
                            headers=provider_auth_headers)
        assert resp.status_code == 200
        assert float(resp.json()["deposit_amount"]) == 15.00


class TestAppointmentWithDeposit:
    def test_appointment_copies_deposit_from_service(self, client, appointment_with_deposit):
        assert float(appointment_with_deposit["deposit_amount"]) == 10.00

    def test_appointment_has_service_base_price(self, client, auth_headers,
                                                 appointment_with_deposit):
        appt_id = appointment_with_deposit["id"]
        resp = client.get(f"/appointments/{appt_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert float(data["service_base_price"]) == 65.00
        assert float(data["deposit_amount"]) == 10.00

    def test_appointment_list_includes_deposit_and_base_price(self, client, auth_headers,
                                                               appointment_with_deposit):
        resp = client.get("/appointments/client", headers=auth_headers)
        items = resp.json()["items"]
        assert float(items[0]["deposit_amount"]) == 10.00
        assert float(items[0]["service_base_price"]) == 65.00

    def test_appointment_without_service_has_null_amounts(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        resp = client.get(f"/appointments/{appt_id}", headers=auth_headers)
        assert resp.json()["deposit_amount"] is None
        assert resp.json()["service_base_price"] is None


class TestDepositPaymentValidation:
    def test_deposit_correct_amount_accepted(self, client, auth_headers, appointment_with_deposit):
        resp = client.post("/payments", json={
            "appointment_id": appointment_with_deposit["id"],
            "amount": 10.00,
            "currency": "eur",
            "payment_type": "deposit",
        }, headers=auth_headers)
        assert resp.status_code == 201

    def test_deposit_wrong_amount_rejected(self, client, auth_headers, appointment_with_deposit):
        resp = client.post("/payments", json={
            "appointment_id": appointment_with_deposit["id"],
            "amount": 20.00,   # mauvais montant
            "currency": "eur",
            "payment_type": "deposit",
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_deposit_no_deposit_amount_on_service_any_amount_accepted(
            self, client, auth_headers, appointment):
        # Service sans deposit_amount → pas de validation du montant
        resp = client.post("/payments", json={
            "appointment_id": appointment["id"],
            "amount": 999.00,
            "currency": "eur",
            "payment_type": "deposit",
        }, headers=auth_headers)
        assert resp.status_code == 201


class TestBalancePaymentValidation:
    def test_balance_correct_amount_accepted(self, client, auth_headers,
                                              provider_auth_headers, appointment_with_deposit):
        appt_id = appointment_with_deposit["id"]
        _prepare_and_confirm(client, auth_headers, appt_id, "pi_bal_ok", "ch_bal_ok")

        # Solde attendu = 65 - 10 = 55
        resp = client.post("/payments", json={
            "appointment_id": appt_id,
            "amount": 55.00,
            "currency": "eur",
            "payment_type": "balance",
        }, headers=auth_headers)
        assert resp.status_code == 201

    def test_balance_wrong_amount_rejected(self, client, auth_headers,
                                            appointment_with_deposit):
        appt_id = appointment_with_deposit["id"]
        _prepare_and_confirm(client, auth_headers, appt_id, "pi_bal_err", "ch_bal_err")

        resp = client.post("/payments", json={
            "appointment_id": appt_id,
            "amount": 30.00,   # mauvais montant
            "currency": "eur",
            "payment_type": "balance",
        }, headers=auth_headers)
        assert resp.status_code == 400


class TestCompleteTriggersInvoice:
    def test_complete_generates_invoice_with_base_price(self, client, auth_headers,
                                                         provider_auth_headers,
                                                         appointment_with_deposit):
        appt_id = appointment_with_deposit["id"]
        _prepare_and_confirm(client, auth_headers, appt_id, "pi_inv", "ch_inv")

        client.post(f"/appointments/{appt_id}/complete", headers=provider_auth_headers)

        resp = client.get(f"/appointments/{appt_id}/invoice", headers=auth_headers)
        assert resp.status_code == 200
        assert float(resp.json()["total_amount"]) == 65.00

    def test_complete_invoice_has_stripe_receipt_url(self, client, auth_headers,
                                                      provider_auth_headers,
                                                      appointment_with_deposit):
        appt_id = appointment_with_deposit["id"]
        _prepare_and_confirm(client, auth_headers, appt_id, "pi_url", "ch_url")

        client.post(f"/appointments/{appt_id}/complete", headers=provider_auth_headers)

        resp = client.get(f"/appointments/{appt_id}/invoice", headers=auth_headers)
        assert resp.json()["pdf_url"] == "https://pay.stripe.com/receipts/test"
