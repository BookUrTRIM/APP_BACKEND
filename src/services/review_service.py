import logging
from typing import List, Tuple

from dtos.review.review_create_dto import ReviewCreateDTO
from dtos.review.review_response_dto import ReviewResponseDTO
from enums.appointment_enum import AppointmentStatus
from exceptions.appointment_exceptions import AppointmentNotEligibleForReview, AppointmentNotFound
from exceptions.client_exceptions import ClientNotFound
from exceptions.review_exceptions import ReviewAccessDenied, ReviewAlreadyExists, ReviewNotFound
from mappers.review_mapper import ReviewMapper
from repositories.appointment_repository import AppointmentRepository
from repositories.client_repository import ClientRepository
from repositories.review_repository import ReviewRepository

logger = logging.getLogger(__name__)


class ReviewService:
    @staticmethod
    def create(user_account_id: int, dto: ReviewCreateDTO) -> ReviewResponseDTO:
        appointment = AppointmentRepository.get_by_id(dto.appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        if appointment.status != AppointmentStatus.COMPLETED:
            raise AppointmentNotEligibleForReview()

        client = ClientRepository.get_by_user_account_id(user_account_id)
        if not client or client.id != appointment.client_id:
            raise ReviewAccessDenied()

        if ReviewRepository.get_by_appointment(dto.appointment_id):
            raise ReviewAlreadyExists()

        review = ReviewRepository.create(dto)
        logger.info("Avis créé : id=%d appointment_id=%d rating=%d", review.id, review.appointment_id, review.rating)
        return ReviewMapper.model_to_dto(review)

    @staticmethod
    def get_by_appointment(appointment_id: int) -> ReviewResponseDTO:
        review = ReviewRepository.get_by_appointment(appointment_id)
        if not review:
            raise ReviewNotFound()
        return ReviewMapper.model_to_dto(review)

    @staticmethod
    def list_by_provider(
        provider_id: int,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[ReviewResponseDTO], int]:
        reviews, total = ReviewRepository.list_by_provider(provider_id, page=page, limit=limit)
        return [ReviewMapper.model_to_dto(r) for r in reviews], total
