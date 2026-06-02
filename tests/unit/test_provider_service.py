"""
Tests unitaires — ProviderService (profil + Stripe Connect)
"""
from unittest.mock import MagicMock, patch

import pytest

from exceptions.provider_exceptions import (
    ProviderAlreadyExists,
    ProviderNotFound,
    StripeConnectAlreadyExists,
    StripeConnectNotConfigured,
)


def _make_provider(id=1, user_account_id=100, stripe_account_id=None):
    p = MagicMock()
    p.id = id
    p.user_account_id = user_account_id
    p.stripe_account_id = stripe_account_id
    return p


class TestCreate:
    def test_should_raise_when_profile_already_exists(self):
        from services.provider_service import ProviderService
        from dtos.provider.provider_create_dto import ProviderCreateDTO

        dto = ProviderCreateDTO(first_name="Léa", last_name="Martin")
        with patch("services.provider_service.ProviderRepository") as mock_repo:
            mock_repo.get_by_user_account_id.return_value = MagicMock()

            with pytest.raises(ProviderAlreadyExists):
                ProviderService.create(user_account_id=100, dto=dto)

    def test_should_create_when_no_existing_profile(self):
        from services.provider_service import ProviderService
        from dtos.provider.provider_create_dto import ProviderCreateDTO

        dto = ProviderCreateDTO(first_name="Léa", last_name="Martin")
        provider = _make_provider()
        with patch("services.provider_service.ProviderRepository") as mock_repo, \
             patch("services.provider_service.ProviderMapper") as mock_mapper:
            mock_repo.get_by_user_account_id.return_value = None
            mock_repo.create.return_value = provider
            mock_mapper.model_to_dto.return_value = MagicMock(id=1)

            result = ProviderService.create(user_account_id=100, dto=dto)

            mock_repo.create.assert_called_once()
            assert result.id == 1


class TestCreateConnectAccount:
    def test_should_raise_when_provider_not_found(self):
        from services.provider_service import ProviderService

        with patch("services.provider_service.ProviderRepository") as mock_repo:
            mock_repo.get_by_user_account_id.return_value = None

            with pytest.raises(ProviderNotFound):
                ProviderService.create_connect_account(user_account_id=99)

    def test_should_raise_when_account_already_exists(self):
        from services.provider_service import ProviderService

        with patch("services.provider_service.ProviderRepository") as mock_repo:
            mock_repo.get_by_user_account_id.return_value = _make_provider(
                stripe_account_id="acct_existing"
            )

            with pytest.raises(StripeConnectAlreadyExists):
                ProviderService.create_connect_account(user_account_id=100)

    def test_should_create_stripe_account_and_save(self):
        from services.provider_service import ProviderService

        mock_account = MagicMock()
        mock_account.id = "acct_new_123"
        updated_provider = _make_provider(stripe_account_id="acct_new_123")

        with patch("services.provider_service.ProviderRepository") as mock_repo, \
             patch("services.provider_service.ProviderMapper") as mock_mapper, \
             patch("stripe.Account.create", return_value=mock_account):
            mock_repo.get_by_user_account_id.return_value = _make_provider(stripe_account_id=None)
            mock_repo.set_stripe_account.return_value = updated_provider
            mock_mapper.model_to_dto.return_value = MagicMock(stripe_account_id="acct_new_123")

            result = ProviderService.create_connect_account(user_account_id=100)

            mock_repo.set_stripe_account.assert_called_once_with(1, "acct_new_123")
            assert result.stripe_account_id == "acct_new_123"


class TestGetOnboardingLink:
    def test_should_raise_when_provider_not_found(self):
        from services.provider_service import ProviderService

        with patch("services.provider_service.ProviderRepository") as mock_repo:
            mock_repo.get_by_user_account_id.return_value = None

            with pytest.raises(ProviderNotFound):
                ProviderService.get_onboarding_link(user_account_id=99)

    def test_should_raise_when_stripe_not_configured(self):
        from services.provider_service import ProviderService

        with patch("services.provider_service.ProviderRepository") as mock_repo:
            mock_repo.get_by_user_account_id.return_value = _make_provider(stripe_account_id=None)

            with pytest.raises(StripeConnectNotConfigured):
                ProviderService.get_onboarding_link(user_account_id=100)

    def test_should_return_onboarding_url(self):
        from services.provider_service import ProviderService

        mock_link = MagicMock()
        mock_link.url = "https://connect.stripe.com/test"

        with patch("services.provider_service.ProviderRepository") as mock_repo, \
             patch("stripe.AccountLink.create", return_value=mock_link):
            mock_repo.get_by_user_account_id.return_value = _make_provider(
                stripe_account_id="acct_existing"
            )

            url = ProviderService.get_onboarding_link(user_account_id=100)

            assert url == "https://connect.stripe.com/test"
