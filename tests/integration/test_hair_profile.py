"""
Tests d'intégration — Profil capillaire client
"""

HAIR_PROFILE_PAYLOAD = {
    "hair_type": "bouclé",
    "hair_length": "long",
}


class TestHairProfile:
    def test_get_hair_profile_null_when_not_set(self, client, auth_headers, client_profile):
        # Act
        resp = client.get("/clients/me/hair-profile", headers=auth_headers)

        # Assert
        assert resp.status_code == 200
        assert resp.json() is None

    def test_create_hair_profile_success(self, client, auth_headers, client_profile):
        # Act
        resp = client.put("/clients/me/hair-profile",
                          json=HAIR_PROFILE_PAYLOAD,
                          headers=auth_headers)

        # Assert
        assert resp.status_code == 200
        data = resp.json()
        assert data["hair_type"] == "bouclé"
        assert data["hair_length"] == "long"
        assert data["client_id"] == client_profile["id"]

    def test_update_hair_profile_success(self, client, auth_headers, client_profile):
        # Arrange
        client.put("/clients/me/hair-profile", json=HAIR_PROFILE_PAYLOAD, headers=auth_headers)

        # Act
        resp = client.put("/clients/me/hair-profile",
                          json={"hair_type": "lisse", "hair_length": "court"},
                          headers=auth_headers)

        # Assert
        assert resp.status_code == 200
        assert resp.json()["hair_type"] == "lisse"
        assert resp.json()["hair_length"] == "court"

    def test_get_hair_profile_after_creation(self, client, auth_headers, client_profile):
        # Arrange
        client.put("/clients/me/hair-profile", json=HAIR_PROFILE_PAYLOAD, headers=auth_headers)

        # Act
        resp = client.get("/clients/me/hair-profile", headers=auth_headers)

        # Assert
        assert resp.status_code == 200
        assert resp.json()["hair_type"] == "bouclé"

    def test_hair_profile_unauthorized(self, client):
        resp = client.get("/clients/me/hair-profile")
        assert resp.status_code == 401

    def test_create_hair_profile_invalid_type(self, client, auth_headers, client_profile):
        resp = client.put("/clients/me/hair-profile",
                          json={"hair_type": "invalide", "hair_length": "long"},
                          headers=auth_headers)
        assert resp.status_code == 422
