"""
Tests d'intégration — Questions de service & calcul de durée
"""

QUESTION_PAYLOAD = {
    "question": "Type de cheveux ?",
    "options": [
        {"label": "Lisse", "extra_minutes": 0},
        {"label": "Bouclé", "extra_minutes": 15},
        {"label": "Crépu", "extra_minutes": 30},
    ],
    "order": 1,
}


class TestServiceQuestions:
    def test_create_question_success(self, client, provider_auth_headers, service):
        # Arrange / Act
        resp = client.post(
            f"/services/{service['id']}/questions",
            json=QUESTION_PAYLOAD,
            headers=provider_auth_headers,
        )
        # Assert
        assert resp.status_code == 201
        data = resp.json()
        assert data["question"] == "Type de cheveux ?"
        assert len(data["options"]) == 3
        assert data["options"][1]["label"] == "Bouclé"
        assert data["options"][1]["extra_minutes"] == 15

    def test_create_question_unauthorized(self, client, service):
        resp = client.post(f"/services/{service['id']}/questions", json=QUESTION_PAYLOAD)
        assert resp.status_code == 401

    def test_create_question_service_not_found(self, client, provider_auth_headers):
        resp = client.post("/services/9999/questions", json=QUESTION_PAYLOAD,
                           headers=provider_auth_headers)
        assert resp.status_code == 404

    def test_list_questions(self, client, provider_auth_headers, service):
        # Arrange
        client.post(f"/services/{service['id']}/questions",
                    json=QUESTION_PAYLOAD, headers=provider_auth_headers)
        client.post(f"/services/{service['id']}/questions",
                    json={**QUESTION_PAYLOAD, "question": "Longueur ?", "order": 2},
                    headers=provider_auth_headers)

        # Act
        resp = client.get(f"/services/{service['id']}/questions")

        # Assert
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["order"] == 1

    def test_list_questions_empty(self, client, service):
        resp = client.get(f"/services/{service['id']}/questions")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_update_question(self, client, provider_auth_headers, service):
        # Arrange
        create = client.post(f"/services/{service['id']}/questions",
                             json=QUESTION_PAYLOAD, headers=provider_auth_headers)
        qid = create.json()["id"]

        # Act
        resp = client.put(f"/services/questions/{qid}",
                          json={"question": "Type de cheveux modifié ?"},
                          headers=provider_auth_headers)

        # Assert
        assert resp.status_code == 200
        assert resp.json()["question"] == "Type de cheveux modifié ?"

    def test_delete_question(self, client, provider_auth_headers, service):
        # Arrange
        create = client.post(f"/services/{service['id']}/questions",
                             json=QUESTION_PAYLOAD, headers=provider_auth_headers)
        qid = create.json()["id"]

        # Act
        resp = client.delete(f"/services/questions/{qid}", headers=provider_auth_headers)

        # Assert
        assert resp.status_code == 204
        assert client.get(f"/services/{service['id']}/questions").json() == []

    def test_delete_question_forbidden(self, client, auth_headers, provider_auth_headers, service):
        create = client.post(f"/services/{service['id']}/questions",
                             json=QUESTION_PAYLOAD, headers=provider_auth_headers)
        qid = create.json()["id"]
        resp = client.delete(f"/services/questions/{qid}", headers=auth_headers)
        assert resp.status_code == 403


class TestCalculateDuration:
    def test_calculate_duration_no_answers(self, client, service):
        # Arrange / Act — aucune réponse, durée = default_duration
        resp = client.post(f"/services/{service['id']}/calculate-duration",
                           json={"answers": []})

        # Assert
        assert resp.status_code == 200
        assert resp.json()["duration"] == service["default_duration"]

    def test_calculate_duration_with_answers(self, client, provider_auth_headers, service):
        # Arrange
        create_q = client.post(f"/services/{service['id']}/questions",
                               json=QUESTION_PAYLOAD, headers=provider_auth_headers)
        qid = create_q.json()["id"]

        # Act — option index 1 = "Bouclé" (+15 min)
        resp = client.post(f"/services/{service['id']}/calculate-duration",
                           json={"answers": [{"question_id": qid, "option_index": 1}]})

        # Assert
        assert resp.status_code == 200
        assert resp.json()["duration"] == service["default_duration"] + 15

    def test_calculate_duration_invalid_index(self, client, provider_auth_headers, service):
        # Arrange
        create_q = client.post(f"/services/{service['id']}/questions",
                               json=QUESTION_PAYLOAD, headers=provider_auth_headers)
        qid = create_q.json()["id"]

        # Act — index 99 n'existe pas
        resp = client.post(f"/services/{service['id']}/calculate-duration",
                           json={"answers": [{"question_id": qid, "option_index": 99}]})

        # Assert
        assert resp.status_code == 400

    def test_calculate_duration_service_not_found(self, client):
        resp = client.post("/services/9999/calculate-duration", json={"answers": []})
        assert resp.status_code == 404
