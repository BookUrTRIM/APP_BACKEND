from typing import List, Optional

from sqlalchemy.orm import Session

from daos.service_question_dao import ServiceQuestionDAO
from dtos.service.service_question_create_dto import ServiceQuestionCreateDTO
from dtos.service.service_question_update_dto import ServiceQuestionUpdateDTO
from mappers.service_question_mapper import ServiceQuestionMapper
from models.service_question_model import ServiceQuestionModel


class ServiceQuestionRepository:
    @staticmethod
    def list_by_service(db: Session, service_id: int) -> List[ServiceQuestionModel]:
        rows = (
            db.query(ServiceQuestionDAO)
            .where(ServiceQuestionDAO.service_id == service_id)
            .order_by(ServiceQuestionDAO.order)
            .all()
        )
        return [ServiceQuestionMapper.dao_to_model(row) for row in rows]

    @staticmethod
    def get_by_id(db: Session, question_id: int) -> Optional[ServiceQuestionModel]:
        dao = db.get(ServiceQuestionDAO, question_id)
        return ServiceQuestionMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def create(db: Session, service_id: int, dto: ServiceQuestionCreateDTO) -> ServiceQuestionModel:
        dao = ServiceQuestionDAO(
            service_id=service_id,
            question=dto.question,
            options=[o.model_dump() for o in dto.options],
            order=dto.order,
        )
        db.add(dao)
        db.flush()
        db.refresh(dao)
        return ServiceQuestionMapper.dao_to_model(dao)

    @staticmethod
    def update(db: Session, question_id: int, dto: ServiceQuestionUpdateDTO) -> Optional[ServiceQuestionModel]:
        dao = db.get(ServiceQuestionDAO, question_id)
        if not dao:
            return None

        if dto.question is not None:
            dao.question = dto.question
        if dto.options is not None:
            dao.options = [o.model_dump() for o in dto.options]
        if dto.order is not None:
            dao.order = dto.order

        db.flush()
        db.refresh(dao)
        return ServiceQuestionMapper.dao_to_model(dao)

    @staticmethod
    def delete(db: Session, question_id: int) -> bool:
        dao = db.get(ServiceQuestionDAO, question_id)
        if not dao:
            return False
        db.delete(dao)
        db.flush()
        return True
