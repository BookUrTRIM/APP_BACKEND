from typing import List, Optional

from daos.service_question_dao import ServiceQuestionDAO
from dtos.service.service_question_create_dto import ServiceQuestionCreateDTO
from dtos.service.service_question_update_dto import ServiceQuestionUpdateDTO
from mappers.service_question_mapper import ServiceQuestionMapper
from models.service_question_model import ServiceQuestionModel
from shared.db import get_db_session


class ServiceQuestionRepository:
    @staticmethod
    def list_by_service(service_id: int) -> List[ServiceQuestionModel]:
        session = get_db_session()
        rows = (
            session.query(ServiceQuestionDAO)
            .where(ServiceQuestionDAO.service_id == service_id)
            .order_by(ServiceQuestionDAO.order)
            .all()
        )
        return [ServiceQuestionMapper.dao_to_model(row) for row in rows]

    @staticmethod
    def get_by_id(question_id: int) -> Optional[ServiceQuestionModel]:
        session = get_db_session()
        dao = session.get(ServiceQuestionDAO, question_id)
        return ServiceQuestionMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def create(service_id: int, dto: ServiceQuestionCreateDTO) -> ServiceQuestionModel:
        session = get_db_session()
        dao = ServiceQuestionDAO(
            service_id=service_id,
            question=dto.question,
            options=[o.model_dump() for o in dto.options],
            order=dto.order,
        )
        session.add(dao)
        session.commit()
        session.refresh(dao)
        return ServiceQuestionMapper.dao_to_model(dao)

    @staticmethod
    def update(question_id: int, dto: ServiceQuestionUpdateDTO) -> Optional[ServiceQuestionModel]:
        session = get_db_session()
        dao = session.get(ServiceQuestionDAO, question_id)
        if not dao:
            return None

        if dto.question is not None:
            dao.question = dto.question
        if dto.options is not None:
            dao.options = [o.model_dump() for o in dto.options]
        if dto.order is not None:
            dao.order = dto.order

        session.commit()
        session.refresh(dao)
        return ServiceQuestionMapper.dao_to_model(dao)

    @staticmethod
    def delete(question_id: int) -> bool:
        session = get_db_session()
        dao = session.get(ServiceQuestionDAO, question_id)
        if not dao:
            return False
        session.delete(dao)
        session.commit()
        return True
