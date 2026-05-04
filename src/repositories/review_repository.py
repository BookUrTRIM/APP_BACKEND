from typing import List, Optional, Tuple

from daos.appointment_dao import AppointmentDAO
from daos.review_dao import ReviewDAO
from dtos.review.review_create_dto import ReviewCreateDTO
from mappers.review_mapper import ReviewMapper
from models.review_model import ReviewModel
from shared.db import get_db_session


class ReviewRepository:
    @staticmethod
    def create(dto: ReviewCreateDTO) -> ReviewModel:
        session = get_db_session()

        dao = ReviewDAO(
            appointment_id=dto.appointment_id,
            rating=dto.rating,
            comment=dto.comment,
        )
        session.add(dao)
        session.commit()
        session.refresh(dao)
        return ReviewMapper.dao_to_model(dao)

    @staticmethod
    def get_by_appointment(appointment_id: int) -> Optional[ReviewModel]:
        session = get_db_session()
        dao = session.query(ReviewDAO).where(ReviewDAO.appointment_id == appointment_id).first()
        return ReviewMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def list_by_provider(
        provider_id: int,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[ReviewModel], int]:
        session = get_db_session()
        # provider_id is derived via appointment (review has no direct FK to provider)
        query = (
            session.query(ReviewDAO)
            .join(AppointmentDAO, AppointmentDAO.id == ReviewDAO.appointment_id)
            .where(AppointmentDAO.provider_id == provider_id)
        )

        total = query.count()
        rows = query.order_by(ReviewDAO.reviewed_at.desc()).limit(limit).offset((page - 1) * limit).all()
        return [ReviewMapper.dao_to_model(row) for row in rows], total
