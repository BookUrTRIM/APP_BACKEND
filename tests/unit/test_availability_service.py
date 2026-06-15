"""
Tests unitaires — AvailabilityService
"""
from unittest.mock import MagicMock, patch

import pytest

from enums.availability_enum import AvailabilityType
from exceptions.availability_exceptions import AvailabilityAccessDenied, AvailabilityNotFound
from exceptions.provider_exceptions import ProviderNotFound


def _make_availability(id=1, provider_id=2):
    a = MagicMock()
    a.id = id
    a.provider_id = provider_id
    return a


def _make_provider(id=2, user_account_id=200):
    p = MagicMock()
    p.id = id
    p.user_account_id = user_account_id
    return p


class TestCreate:
    def test_should_raise_when_no_provider_profile(self):
        from services.availability_service import AvailabilityService
        from dtos.availability.availability_create_dto import AvailabilityCreateDTO
        from datetime import date, time

        dto = AvailabilityCreateDTO(
            day_date=date(2026, 6, 1),
            start_time=time(9, 0),
            end_time=time(18, 0),
            slot_type=AvailabilityType.WORK,
        )
        with patch("services.availability_service.ProviderRepository") as mock_repo:
            mock_repo.get_by_user_account_id.return_value = None

            with pytest.raises(ProviderNotFound):
                AvailabilityService.create(user_account_id=99, dto=dto)

    def test_should_create_when_valid(self):
        from services.availability_service import AvailabilityService
        from dtos.availability.availability_create_dto import AvailabilityCreateDTO
        from datetime import date, time

        dto = AvailabilityCreateDTO(
            day_date=date(2026, 6, 1),
            start_time=time(9, 0),
            end_time=time(18, 0),
            slot_type=AvailabilityType.WORK,
        )
        avail = _make_availability()
        with patch("services.availability_service.ProviderRepository") as mock_provider, \
             patch("services.availability_service.AvailabilityRepository") as mock_avail, \
             patch("services.availability_service.AvailabilityMapper") as mock_mapper:
            mock_provider.get_by_user_account_id.return_value = _make_provider()
            mock_avail.create.return_value = avail
            mock_mapper.model_to_dto.return_value = MagicMock(id=1)

            result = AvailabilityService.create(user_account_id=200, dto=dto)

            mock_avail.create.assert_called_once()
            assert result.id == 1


class TestDelete:
    def test_should_raise_when_not_found(self):
        from services.availability_service import AvailabilityService

        with patch("services.availability_service.AvailabilityRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None

            with pytest.raises(AvailabilityNotFound):
                AvailabilityService.delete(availability_id=99, user_account_id=200)

    def test_should_raise_when_not_owner(self):
        from services.availability_service import AvailabilityService

        with patch("services.availability_service.AvailabilityRepository") as mock_repo, \
             patch("services.availability_service.ProviderRepository") as mock_provider:
            mock_repo.get_by_id.return_value = _make_availability(provider_id=2)
            mock_provider.get_by_user_account_id.return_value = _make_provider(id=99)

            with pytest.raises(AvailabilityAccessDenied):
                AvailabilityService.delete(availability_id=1, user_account_id=999)

    def test_should_delete_when_owner(self):
        from services.availability_service import AvailabilityService

        with patch("services.availability_service.AvailabilityRepository") as mock_repo, \
             patch("services.availability_service.ProviderRepository") as mock_provider:
            mock_repo.get_by_id.return_value = _make_availability(provider_id=2)
            mock_provider.get_by_user_account_id.return_value = _make_provider(id=2)

            AvailabilityService.delete(availability_id=1, user_account_id=200)

            mock_repo.delete.assert_called_once_with(1)
