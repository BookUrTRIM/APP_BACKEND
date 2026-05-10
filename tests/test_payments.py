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
