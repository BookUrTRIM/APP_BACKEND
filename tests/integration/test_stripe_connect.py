"""
Tests d'intégration — Stripe Connect (onboarding prestataire)
"""
from unittest.mock import MagicMock, patch


def _mock_stripe_account(account_id="acct_test_123"):
    account = MagicMock()
    account.id = account_id
    return account


def _mock_account_link(url="https://connect.stripe.com/setup/test"):
    link = MagicMock()
    link.url = url
    return link


class TestStripeConnect:
    def test_create_connect_account_success(self, client, provider_auth_headers, provider_profile):
        # Act
        with patch("stripe.Account.create", return_value=_mock_stripe_account()):
            resp = client.post("/providers/me/stripe-connect", headers=provider_auth_headers)

        # Assert
        assert resp.status_code == 200
        assert resp.json()["stripe_account_id"] == "acct_test_123"

    def test_create_connect_account_unauthorized(self, client):
        resp = client.post("/providers/me/stripe-connect")
        assert resp.status_code == 401

    def test_create_connect_account_already_exists(self, client, provider_auth_headers, provider_profile):
        # Arrange
        with patch("stripe.Account.create", return_value=_mock_stripe_account()):
            client.post("/providers/me/stripe-connect", headers=provider_auth_headers)

        # Act — second call
        with patch("stripe.Account.create", return_value=_mock_stripe_account()):
            resp = client.post("/providers/me/stripe-connect", headers=provider_auth_headers)

        # Assert
        assert resp.status_code == 409

    def test_get_onboarding_link_success(self, client, provider_auth_headers, provider_profile):
        # Arrange — créer d'abord le compte Connect
        with patch("stripe.Account.create", return_value=_mock_stripe_account()):
            client.post("/providers/me/stripe-connect", headers=provider_auth_headers)

        # Act
        with patch("stripe.AccountLink.create", return_value=_mock_account_link()):
            resp = client.get("/providers/me/stripe-connect/onboarding",
                              headers=provider_auth_headers)

        # Assert
        assert resp.status_code == 200
        assert resp.json()["url"] == "https://connect.stripe.com/setup/test"

    def test_get_onboarding_link_not_configured(self, client, provider_auth_headers, provider_profile):
        # Act — sans avoir créé le compte Connect
        resp = client.get("/providers/me/stripe-connect/onboarding",
                          headers=provider_auth_headers)

        # Assert
        assert resp.status_code == 422

    def test_get_onboarding_link_unauthorized(self, client):
        resp = client.get("/providers/me/stripe-connect/onboarding")
        assert resp.status_code == 401

    def test_stripe_account_id_visible_in_provider_profile(self, client, provider_auth_headers, provider_profile):
        # Arrange
        with patch("stripe.Account.create", return_value=_mock_stripe_account("acct_visible")):
            client.post("/providers/me/stripe-connect", headers=provider_auth_headers)

        # Act
        resp = client.get("/providers/me", headers=provider_auth_headers)

        # Assert
        assert resp.status_code == 200
        assert resp.json()["stripe_account_id"] == "acct_visible"
