APPT_PAYLOAD = {
    "provider_id": None,
    "start_at": "2025-12-01T10:00:00Z",
    "end_at": "2025-12-01T11:00:00Z",
    "specific_request": "Coupe courte",
}


class TestBookAppointment:
    def test_book_success(self, client, auth_headers, client_profile, provider_profile):
        resp = client.post("/appointments", json={
            **APPT_PAYLOAD,
            "provider_id": provider_profile["id"],
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert data["client_id"] == client_profile["id"]
        assert data["provider_id"] == provider_profile["id"]

    def test_book_unauthorized(self, client, provider_profile):
        resp = client.post("/appointments", json={**APPT_PAYLOAD, "provider_id": provider_profile["id"]})
        assert resp.status_code == 401

    def test_book_no_client_profile(self, client, auth_headers, provider_profile):
        resp = client.post("/appointments", json={
            **APPT_PAYLOAD,
            "provider_id": provider_profile["id"],
        }, headers=auth_headers)
        assert resp.status_code == 404

    def test_book_invalid_dates(self, client, auth_headers, client_profile, provider_profile):
        resp = client.post("/appointments", json={
            "provider_id": provider_profile["id"],
            "start_at": "2025-12-01T11:00:00Z",
            "end_at": "2025-12-01T10:00:00Z",
        }, headers=auth_headers)
        assert resp.status_code == 422


class TestGetAppointment:
    def test_get_by_client(self, client, auth_headers, appointment):
        resp = client.get(f"/appointments/{appointment['id']}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == appointment["id"]

    def test_get_by_provider(self, client, provider_auth_headers, appointment):
        resp = client.get(f"/appointments/{appointment['id']}", headers=provider_auth_headers)
        assert resp.status_code == 200

    def test_get_unauthorized(self, client, appointment):
        resp = client.get(f"/appointments/{appointment['id']}")
        assert resp.status_code == 401

    def test_get_not_found(self, client, auth_headers, client_profile):
        resp = client.get("/appointments/9999", headers=auth_headers)
        assert resp.status_code == 404


class TestListAppointments:
    def test_list_by_client(self, client, auth_headers, appointment):
        resp = client.get("/appointments/client", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_list_by_client_empty(self, client, auth_headers, client_profile):
        resp = client.get("/appointments/client", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    def test_list_by_client_with_status_filter(self, client, auth_headers, appointment):
        resp = client.get("/appointments/client?status=pending", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

        resp = client.get("/appointments/client?status=confirmed", headers=auth_headers)
        assert resp.json()["total"] == 0

    def test_list_by_provider(self, client, provider_auth_headers, appointment):
        resp = client.get("/appointments/provider", headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    def test_list_by_provider_empty(self, client, provider_auth_headers, provider_profile):
        resp = client.get("/appointments/provider", headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestUpdateAppointment:
    def test_confirm_by_provider(self, client, provider_auth_headers, appointment):
        appt_id = appointment["id"]
        resp = client.patch(f"/appointments/{appt_id}",
                            json={"status": "confirmed"},
                            headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "confirmed"

    def test_complete_by_provider(self, client, provider_auth_headers, confirmed_appointment):
        appt_id = confirmed_appointment["id"]
        resp = client.patch(f"/appointments/{appt_id}",
                            json={"status": "completed"},
                            headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"

    def test_invalid_transition(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        resp = client.patch(f"/appointments/{appt_id}",
                            json={"status": "completed"},
                            headers=auth_headers)
        assert resp.status_code == 400

    def test_update_products_used(self, client, provider_auth_headers, appointment):
        appt_id = appointment["id"]
        resp = client.patch(f"/appointments/{appt_id}",
                            json={"products_used": "Shampoing Kérastase"},
                            headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["products_used"] == "Shampoing Kérastase"


class TestCancelAppointment:
    def test_cancel_by_client(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        resp = client.post(f"/appointments/{appt_id}/cancel", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_cancel_by_provider(self, client, provider_auth_headers, appointment):
        appt_id = appointment["id"]
        resp = client.post(f"/appointments/{appt_id}/cancel", headers=provider_auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_cancel_already_cancelled(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        client.post(f"/appointments/{appt_id}/cancel", headers=auth_headers)
        resp = client.post(f"/appointments/{appt_id}/cancel", headers=auth_headers)
        assert resp.status_code == 409

    def test_cancel_completed(self, client, auth_headers, completed_appointment):
        appt_id = completed_appointment["id"]
        resp = client.post(f"/appointments/{appt_id}/cancel", headers=auth_headers)
        assert resp.status_code == 400


class TestInvoice:
    def test_generate_success(self, client, auth_headers, completed_appointment):
        appt_id = completed_appointment["id"]
        resp = client.post(f"/appointments/{appt_id}/invoice", headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["appointment_id"] == appt_id

    def test_generate_not_completed(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        resp = client.post(f"/appointments/{appt_id}/invoice", headers=auth_headers)
        assert resp.status_code == 400

    def test_generate_already_exists(self, client, auth_headers, completed_appointment):
        appt_id = completed_appointment["id"]
        client.post(f"/appointments/{appt_id}/invoice", headers=auth_headers)
        resp = client.post(f"/appointments/{appt_id}/invoice", headers=auth_headers)
        assert resp.status_code == 409

    def test_get_invoice(self, client, auth_headers, completed_appointment):
        appt_id = completed_appointment["id"]
        client.post(f"/appointments/{appt_id}/invoice", headers=auth_headers)
        resp = client.get(f"/appointments/{appt_id}/invoice", headers=auth_headers)
        assert resp.status_code == 200
        assert float(resp.json()["total_amount"]) == 0.0

    def test_get_invoice_not_found(self, client, auth_headers, appointment):
        resp = client.get(f"/appointments/{appointment['id']}/invoice", headers=auth_headers)
        assert resp.status_code == 404


class TestReview:
    def test_create_review_success(self, client, auth_headers, completed_appointment):
        appt_id = completed_appointment["id"]
        resp = client.post(f"/appointments/{appt_id}/review", json={
            "appointment_id": appt_id,
            "rating": 5,
            "comment": "Excellente prestataire !",
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["rating"] == 5

    def test_create_review_not_completed(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        resp = client.post(f"/appointments/{appt_id}/review", json={
            "appointment_id": appt_id,
            "rating": 4,
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_create_review_already_exists(self, client, auth_headers, completed_appointment):
        appt_id = completed_appointment["id"]
        client.post(f"/appointments/{appt_id}/review", json={
            "appointment_id": appt_id, "rating": 5,
        }, headers=auth_headers)
        resp = client.post(f"/appointments/{appt_id}/review", json={
            "appointment_id": appt_id, "rating": 3,
        }, headers=auth_headers)
        assert resp.status_code == 409

    def test_create_review_wrong_client(self, client, provider_auth_headers, completed_appointment):
        appt_id = completed_appointment["id"]
        resp = client.post(f"/appointments/{appt_id}/review", json={
            "appointment_id": appt_id, "rating": 1,
        }, headers=provider_auth_headers)
        assert resp.status_code == 403

    def test_get_review(self, client, auth_headers, completed_appointment):
        appt_id = completed_appointment["id"]
        client.post(f"/appointments/{appt_id}/review", json={
            "appointment_id": appt_id, "rating": 5,
        }, headers=auth_headers)
        resp = client.get(f"/appointments/{appt_id}/review")
        assert resp.status_code == 200
        assert resp.json()["rating"] == 5

    def test_get_review_not_found(self, client, appointment):
        resp = client.get(f"/appointments/{appointment['id']}/review")
        assert resp.status_code == 404

    def test_invalid_rating(self, client, auth_headers, completed_appointment):
        appt_id = completed_appointment["id"]
        resp = client.post(f"/appointments/{appt_id}/review", json={
            "appointment_id": appt_id, "rating": 6,
        }, headers=auth_headers)
        assert resp.status_code == 422
