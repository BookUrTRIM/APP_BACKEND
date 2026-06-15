from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from daos.appointment_dao import AppointmentDAO
from daos.review_dao import ReviewDAO
from dtos.review.review_create_dto import ReviewCreateDTO
from mappers.review_mapper import ReviewMapper
from models.review_model import ReviewModel


class ReviewRepository:
    @staticmethod
    def create(db: Session, dto: ReviewCreateDTO) -> ReviewModel:
        dao = ReviewDAO(
            appointment_id=dto.appointment_id,
            rating=dto.rating,
            comment=dto.comment,
        )
        db.add(dao)
        db.flush()
        db.refresh(dao)
        return ReviewMapper.dao_to_model(dao)

    @staticmethod
    def get_by_appointment(db: Session, appointment_id: int) -> Optional[ReviewModel]:
        dao = db.query(ReviewDAO).where(ReviewDAO.appointment_id == appointment_id).first()
        return ReviewMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def list_by_provider(db: Session, provider_id: int, page: int = 1, limit: int = 20) -> Tuple[List[ReviewModel], int]:
        query = (
            db.query(ReviewDAO)
            .join(AppointmentDAO, AppointmentDAO.id == ReviewDAO.appointment_id)
            .where(AppointmentDAO.provider_id == provider_id)
        )
        total = query.count()
        rows = query.order_by(ReviewDAO.reviewed_at.desc()).limit(limit).offset((page - 1) * limit).all()
        return [ReviewMapper.dao_to_model(row) for row in rows], total
