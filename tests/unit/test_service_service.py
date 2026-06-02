"""
Tests unitaires — ServiceService
"""
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from exceptions.provider_exceptions import ProviderNotFound
from exceptions.service_exceptions import ServiceAccessDenied, ServiceNotFound


def _make_service(id=1, provider_id=2):
    s = MagicMock()
    s.id = id
    s.provider_id = provider_id
    s.name = "Coupe femme"
    return s


def _make_provider(id=2, user_account_id=200):
    p = MagicMock()
    p.id = id
    p.user_account_id = user_account_id
    return p


class TestCreate:
    def test_should_raise_when_no_provider_profile(self):
        from services.service_service import ServiceService
        from dtos.service.service_create_dto import ServiceCreateDTO

        dto = ServiceCreateDTO(name="Coupe", default_duration=60, base_price=Decimal("45.00"))
        with patch("services.service_service.ProviderRepository") as mock_repo:
            mock_repo.get_by_user_account_id.return_value = None

            with pytest.raises(ProviderNotFound):
                ServiceService.create(user_account_id=99, dto=dto)

    def test_should_create_when_valid(self):
        from services.service_service import ServiceService
        from dtos.service.service_create_dto import ServiceCreateDTO

        dto = ServiceCreateDTO(name="Coupe", default_duration=60, base_price=Decimal("45.00"))
        service = _make_service()
        with patch("services.service_service.ProviderRepository") as mock_provider, \
             patch("services.service_service.ServiceRepository") as mock_service, \
             patch("services.service_service.ServiceMapper") as mock_mapper:
            mock_provider.get_by_user_account_id.return_value = _make_provider()
            mock_service.create.return_value = service
            mock_dto = MagicMock()
            mock_dto.id = 1
            mock_dto.name = "Coupe"
            mock_mapper.model_to_dto.return_value = mock_dto

            result = ServiceService.create(user_account_id=200, dto=dto)

            mock_service.create.assert_called_once_with(dto, 2)
            assert result.name == "Coupe"


class TestUpdate:
    def test_should_raise_when_service_not_found(self):
        from services.service_service import ServiceService
        from dtos.service.service_update_dto import ServiceUpdateDTO

        dto = ServiceUpdateDTO(name="Nouveau nom")
        with patch("services.service_service.ServiceRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None

            with pytest.raises(ServiceNotFound):
                ServiceService.update(service_id=99, user_account_id=200, dto=dto)

    def test_should_raise_when_not_owner(self):
        from services.service_service import ServiceService
        from dtos.service.service_update_dto import ServiceUpdateDTO

        dto = ServiceUpdateDTO(name="Hack")
        with patch("services.service_service.ServiceRepository") as mock_service, \
             patch("services.service_service.ProviderRepository") as mock_provider:
            mock_service.get_by_id.return_value = _make_service(provider_id=2)
            mock_provider.get_by_user_account_id.return_value = _make_provider(id=99)

            with pytest.raises(ServiceAccessDenied):
                ServiceService.update(service_id=1, user_account_id=999, dto=dto)


class TestDelete:
    def test_should_raise_when_service_not_found(self):
        from services.service_service import ServiceService

        with patch("services.service_service.ServiceRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None

            with pytest.raises(ServiceNotFound):
                ServiceService.delete(service_id=99, user_account_id=200)

    def test_should_delete_when_owner(self):
        from services.service_service import ServiceService

        with patch("services.service_service.ServiceRepository") as mock_service, \
             patch("services.service_service.ProviderRepository") as mock_provider:
            mock_service.get_by_id.return_value = _make_service(provider_id=2)
            mock_provider.get_by_user_account_id.return_value = _make_provider(id=2)

            ServiceService.delete(service_id=1, user_account_id=200)

            mock_service.delete.assert_called_once_with(1)


class TestGet:
    def test_should_raise_when_not_found(self):
        from services.service_service import ServiceService

        with patch("services.service_service.ServiceRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None

            with pytest.raises(ServiceNotFound):
                ServiceService.get(service_id=99)
