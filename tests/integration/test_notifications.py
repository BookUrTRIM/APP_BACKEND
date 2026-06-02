class TestNotifications:
    def test_list_empty(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        resp = client.get(f"/notifications/appointment/{appt_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_send_confirmation(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        resp = client.post(f"/notifications/appointment/{appt_id}",
                           params={"recipient": "client", "notification_type": "confirmation"},
                           headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["recipient"] == "client"
        assert data["notification_type"] == "confirmation"
        assert data["status"] == "sent"

    def test_send_reminder(self, client, provider_auth_headers, appointment):
        appt_id = appointment["id"]
        resp = client.post(f"/notifications/appointment/{appt_id}",
                           params={"recipient": "provider", "notification_type": "reminder"},
                           headers=provider_auth_headers)
        assert resp.status_code == 201
        assert resp.json()["notification_type"] == "reminder"

    def test_send_unauthorized(self, client, appointment):
        appt_id = appointment["id"]
        resp = client.post(f"/notifications/appointment/{appt_id}",
                           params={"recipient": "client", "notification_type": "confirmation"})
        assert resp.status_code == 401

    def test_list_after_send(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        client.post(f"/notifications/appointment/{appt_id}",
                    params={"recipient": "client", "notification_type": "confirmation"},
                    headers=auth_headers)
        client.post(f"/notifications/appointment/{appt_id}",
                    params={"recipient": "provider", "notification_type": "reminder"},
                    headers=auth_headers)

        resp = client.get(f"/notifications/appointment/{appt_id}", headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_update_status(self, client, auth_headers, appointment):
        appt_id = appointment["id"]
        send = client.post(f"/notifications/appointment/{appt_id}",
                           params={"recipient": "client", "notification_type": "confirmation"},
                           headers=auth_headers)
        notif_id = send.json()["id"]

        resp = client.patch(f"/notifications/{notif_id}/status",
                            params={"status": "failed"},
                            headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "failed"

    def test_update_status_not_found(self, client, auth_headers, client_profile):
        resp = client.patch("/notifications/9999/status",
                            params={"status": "sent"},
                            headers=auth_headers)
        assert resp.status_code == 404
