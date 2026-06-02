"""
Tests unitaires — AppointmentService
Toutes les dépendances (repositories) sont mockées.
"""
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from enums.appointment_enum import AppointmentStatus
from exceptions.appointment_exceptions import (
    AppointmentAccessDenied,
    AppointmentAlreadyCancelled,
    AppointmentNotFound,
    InvalidStatusTransition,
    TooManyPendingAppointments,
)
from exceptions.client_exceptions import ClientNotFound
from exceptions.provider_exceptions import ProviderNotFound


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_appointment(status=AppointmentStatus.PENDING, client_id=1, provider_id=2):
    appt = MagicMock()
    appt.id = 10
    appt.client_id = client_id
    appt.provider_id = provider_id
    appt.status = status
    appt.start_at = datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc)
    appt.end_at = datetime(2026, 6, 1, 11, 0, tzinfo=timezone.utc)
    return appt


def _make_client(id=1, user_account_id=100):
    c = MagicMock()
    c.id = id
    c.user_account_id = user_account_id
    return c


def _make_provider(id=2, user_account_id=200):
    p = MagicMock()
    p.id = id
    p.user_account_id = user_account_id
    p.stripe_account_id = None
    return p


# ── book ──────────────────────────────────────────────────────────────────────

class TestBook:
    def test_should_raise_when_client_not_found(self):
        # Arrange
        from services.appointment_service import AppointmentService
        from dtos.appointment.appointment_create_dto import AppointmentCreateDTO

        dto = AppointmentCreateDTO(
            provider_id=1,
            start_at=datetime(2026, 6, 1, 10, 0),
            end_at=datetime(2026, 6, 1, 11, 0),
        )
        with patch("services.appointment_service.ClientRepository") as mock_client:
            mock_client.get_by_user_account_id.return_value = None

            # Act / Assert
            with pytest.raises(ClientNotFound):
                AppointmentService.book(user_account_id=99, dto=dto)

    def test_should_raise_when_provider_not_found(self):
        # Arrange
        from services.appointment_service import AppointmentService
        from dtos.appointment.appointment_create_dto import AppointmentCreateDTO

        dto = AppointmentCreateDTO(
            provider_id=999,
            start_at=datetime(2026, 6, 1, 10, 0),
            end_at=datetime(2026, 6, 1, 11, 0),
        )
        with patch("services.appointment_service.ClientRepository") as mock_client, \
             patch("services.appointment_service.ProviderRepository") as mock_provider:
            mock_client.get_by_user_account_id.return_value = _make_client()
            mock_provider.get_by_id.return_value = None

            # Act / Assert
            with pytest.raises(ProviderNotFound):
                AppointmentService.book(user_account_id=100, dto=dto)

    def test_should_raise_when_too_many_pending(self):
        # Arrange
        from services.appointment_service import AppointmentService
        from dtos.appointment.appointment_create_dto import AppointmentCreateDTO

        dto = AppointmentCreateDTO(
            provider_id=2,
            start_at=datetime(2026, 6, 1, 10, 0),
            end_at=datetime(2026, 6, 1, 11, 0),
        )
        with patch("services.appointment_service.ClientRepository") as mock_client, \
             patch("services.appointment_service.ProviderRepository") as mock_provider, \
             patch("services.appointment_service.AppointmentRepository") as mock_repo:
            mock_client.get_by_user_account_id.return_value = _make_client()
            mock_provider.get_by_id.return_value = _make_provider()
            mock_repo.count_pending_by_client.return_value = 2

            # Act / Assert
            with pytest.raises(TooManyPendingAppointments):
                AppointmentService.book(user_account_id=100, dto=dto)

    def test_should_succeed_when_data_is_valid(self):
        # Arrange
        from services.appointment_service import AppointmentService
        from dtos.appointment.appointment_create_dto import AppointmentCreateDTO

        dto = AppointmentCreateDTO(
            provider_id=2,
            start_at=datetime(2026, 6, 1, 10, 0),
            end_at=datetime(2026, 6, 1, 11, 0),
        )
        appt = _make_appointment()
        with patch("services.appointment_service.ClientRepository") as mock_client, \
             patch("services.appointment_service.ProviderRepository") as mock_provider, \
             patch("services.appointment_service.AppointmentRepository") as mock_repo, \
             patch("services.appointment_service.AppointmentMapper") as mock_mapper:
            mock_client.get_by_user_account_id.return_value = _make_client()
            mock_provider.get_by_id.return_value = _make_provider()
            mock_repo.count_pending_by_client.return_value = 0
            mock_repo.create.return_value = appt
            mock_mapper.model_to_dto.return_value = MagicMock(id=10, status="pending")

            # Act
            result = AppointmentService.book(user_account_id=100, dto=dto)

            # Assert
            mock_repo.create.assert_called_once()
            assert result.id == 10


# ── status transitions ────────────────────────────────────────────────────────

class TestStatusTransitions:
    @pytest.mark.parametrize("current,target,should_raise", [
        (AppointmentStatus.PENDING,    AppointmentStatus.CONFIRMED,  False),
        (AppointmentStatus.PENDING,    AppointmentStatus.CANCELLED,  False),
        (AppointmentStatus.PENDING,    AppointmentStatus.COMPLETED,  True),
        (AppointmentStatus.CONFIRMED,  AppointmentStatus.COMPLETED,  False),
        (AppointmentStatus.CONFIRMED,  AppointmentStatus.CANCELLED,  False),
        (AppointmentStatus.COMPLETED,  AppointmentStatus.CANCELLED,  True),
        (AppointmentStatus.CANCELLED,  AppointmentStatus.CONFIRMED,  True),
        (AppointmentStatus.EXPIRED,    AppointmentStatus.PENDING,    True),
    ])
    def test_transition_validity(self, current, target, should_raise):
        # Arrange
        from services.appointment_service import AppointmentService

        # Act / Assert
        if should_raise:
            with pytest.raises(InvalidStatusTransition):
                AppointmentService._assert_valid_transition(current, target)
        else:
            AppointmentService._assert_valid_transition(current, target)


# ── cancel_by_client ──────────────────────────────────────────────────────────

class TestCancelByClient:
    def test_should_raise_when_appointment_not_found(self):
        from services.appointment_service import AppointmentService

        with patch("services.appointment_service.AppointmentRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None
            with pytest.raises(AppointmentNotFound):
                AppointmentService.cancel_by_client(appointment_id=99, user_account_id=100)

    def test_should_raise_when_already_cancelled(self):
        from services.appointment_service import AppointmentService

        with patch("services.appointment_service.AppointmentRepository") as mock_repo:
            mock_repo.get_by_id.return_value = _make_appointment(status=AppointmentStatus.CANCELLED)
            with pytest.raises(AppointmentAlreadyCancelled):
                AppointmentService.cancel_by_client(appointment_id=10, user_account_id=100)

    def test_should_raise_when_not_the_client(self):
        from services.appointment_service import AppointmentService

        with patch("services.appointment_service.AppointmentRepository") as mock_repo, \
             patch("services.appointment_service.ClientRepository") as mock_client:
            mock_repo.get_by_id.return_value = _make_appointment(client_id=1)
            mock_client.get_by_user_account_id.return_value = _make_client(id=99)

            with pytest.raises(AppointmentAccessDenied):
                AppointmentService.cancel_by_client(appointment_id=10, user_account_id=200)


# ── cancel_by_provider ────────────────────────────────────────────────────────

class TestCancelByProvider:
    def test_should_raise_when_not_the_provider(self):
        from services.appointment_service import AppointmentService

        with patch("services.appointment_service.AppointmentRepository") as mock_repo, \
             patch("services.appointment_service.ProviderRepository") as mock_provider:
            mock_repo.get_by_id.return_value = _make_appointment(provider_id=2)
            mock_provider.get_by_user_account_id.return_value = _make_provider(id=99)

            with pytest.raises(AppointmentAccessDenied):
                AppointmentService.cancel_by_provider(appointment_id=10, user_account_id=200)
