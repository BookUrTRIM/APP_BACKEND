"""
Tests unitaires — ReviewService
"""
from unittest.mock import MagicMock, patch

import pytest

from enums.appointment_enum import AppointmentStatus
from exceptions.appointment_exceptions import AppointmentNotFound
from exceptions.review_exceptions import (
    AppointmentNotEligibleForReview,
    ReviewAccessDenied,
    ReviewAlreadyExists,
    ReviewNotFound,
)


def _make_appointment(status=AppointmentStatus.COMPLETED, client_id=1):
    appt = MagicMock()
    appt.id = 10
    appt.client_id = client_id
    appt.status = status
    return appt


class TestCreateReview:
    def test_should_raise_when_appointment_not_found(self):
        # Arrange
        from services.review_service import ReviewService
        from dtos.review.review_create_dto import ReviewCreateDTO

        dto = ReviewCreateDTO(appointment_id=999, rating=5)
        with patch("services.review_service.AppointmentRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None

            # Act / Assert
            with pytest.raises(AppointmentNotFound):
                ReviewService.create(user_account_id=100, dto=dto)

    def test_should_raise_when_appointment_not_completed(self):
        # Arrange
        from services.review_service import ReviewService
        from dtos.review.review_create_dto import ReviewCreateDTO

        dto = ReviewCreateDTO(appointment_id=10, rating=5)
        with patch("services.review_service.AppointmentRepository") as mock_repo:
            mock_repo.get_by_id.return_value = _make_appointment(status=AppointmentStatus.CONFIRMED)

            # Act / Assert
            with pytest.raises(AppointmentNotEligibleForReview):
                ReviewService.create(user_account_id=100, dto=dto)

    def test_should_raise_when_not_the_client(self):
        # Arrange
        from services.review_service import ReviewService
        from dtos.review.review_create_dto import ReviewCreateDTO

        dto = ReviewCreateDTO(appointment_id=10, rating=5)
        wrong_client = MagicMock()
        wrong_client.id = 99

        with patch("services.review_service.AppointmentRepository") as mock_appt, \
             patch("services.review_service.ClientRepository") as mock_client:
            mock_appt.get_by_id.return_value = _make_appointment(client_id=1)
            mock_client.get_by_user_account_id.return_value = wrong_client

            # Act / Assert
            with pytest.raises(ReviewAccessDenied):
                ReviewService.create(user_account_id=200, dto=dto)

    def test_should_raise_when_review_already_exists(self):
        # Arrange
        from services.review_service import ReviewService
        from dtos.review.review_create_dto import ReviewCreateDTO

        dto = ReviewCreateDTO(appointment_id=10, rating=5)
        correct_client = MagicMock()
        correct_client.id = 1

        with patch("services.review_service.AppointmentRepository") as mock_appt, \
             patch("services.review_service.ClientRepository") as mock_client, \
             patch("services.review_service.ReviewRepository") as mock_review:
            mock_appt.get_by_id.return_value = _make_appointment(client_id=1)
            mock_client.get_by_user_account_id.return_value = correct_client
            mock_review.get_by_appointment.return_value = MagicMock()

            # Act / Assert
            with pytest.raises(ReviewAlreadyExists):
                ReviewService.create(user_account_id=100, dto=dto)

    def test_should_succeed_when_all_conditions_met(self):
        # Arrange
        from services.review_service import ReviewService
        from dtos.review.review_create_dto import ReviewCreateDTO

        dto = ReviewCreateDTO(appointment_id=10, rating=5, comment="Parfait !")
        correct_client = MagicMock()
        correct_client.id = 1
        new_review = MagicMock()
        new_review.id = 1
        new_review.rating = 5

        with patch("services.review_service.AppointmentRepository") as mock_appt, \
             patch("services.review_service.ClientRepository") as mock_client, \
             patch("services.review_service.ReviewRepository") as mock_review, \
             patch("services.review_service.ReviewMapper") as mock_mapper:
            mock_appt.get_by_id.return_value = _make_appointment(client_id=1)
            mock_client.get_by_user_account_id.return_value = correct_client
            mock_review.get_by_appointment.return_value = None
            mock_review.create.return_value = new_review
            mock_mapper.model_to_dto.return_value = MagicMock(rating=5)

            # Act
            result = ReviewService.create(user_account_id=100, dto=dto)

            # Assert
            mock_review.create.assert_called_once()
            assert result.rating == 5


class TestGetByAppointment:
    def test_should_raise_when_review_not_found(self):
        # Arrange
        from services.review_service import ReviewService

        with patch("services.review_service.ReviewRepository") as mock_repo:
            mock_repo.get_by_appointment.return_value = None

            # Act / Assert
            with pytest.raises(ReviewNotFound):
                ReviewService.get_by_appointment(appointment_id=10)
