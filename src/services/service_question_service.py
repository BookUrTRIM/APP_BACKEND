import logging
from typing import List

from sqlalchemy.orm import Session

from dtos.service.duration_calculate_dto import DurationCalculateDTO
from dtos.service.duration_response_dto import DurationResponseDTO
from dtos.service.service_question_create_dto import ServiceQuestionCreateDTO
from dtos.service.service_question_response_dto import ServiceQuestionResponseDTO
from dtos.service.service_question_update_dto import ServiceQuestionUpdateDTO
from exceptions.service_exceptions import ServiceAccessDenied, ServiceNotFound
from exceptions.service_question_exceptions import ServiceQuestionIndexError, ServiceQuestionNotFound
from mappers.service_question_mapper import ServiceQuestionMapper
from repositories.provider_repository import ProviderRepository
from repositories.service_question_repository import ServiceQuestionRepository
from repositories.service_repository import ServiceRepository

logger = logging.getLogger(__name__)


class ServiceQuestionService:
    @staticmethod
    def list(db: Session, service_id: int) -> List[ServiceQuestionResponseDTO]:
        if not ServiceRepository.get_by_id(db, service_id):
            raise ServiceNotFound()
        questions = ServiceQuestionRepository.list_by_service(db, service_id)
        return [ServiceQuestionMapper.model_to_dto(q) for q in questions]

    @staticmethod
    def create(db: Session, service_id: int, user_account_id: int, dto: ServiceQuestionCreateDTO) -> ServiceQuestionResponseDTO:
        service = ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise ServiceNotFound()
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider or provider.id != service.provider_id:
            raise ServiceAccessDenied()
        question = ServiceQuestionRepository.create(db, service_id, dto)
        db.commit()
        logger.info("Question créée : id=%d service_id=%d", question.id, service_id)
        return ServiceQuestionMapper.model_to_dto(question)

    @staticmethod
    def update(db: Session, question_id: int, user_account_id: int, dto: ServiceQuestionUpdateDTO) -> ServiceQuestionResponseDTO:
        question = ServiceQuestionRepository.get_by_id(db, question_id)
        if not question:
            raise ServiceQuestionNotFound()
        service = ServiceRepository.get_by_id(db, question.service_id)
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider or not service or provider.id != service.provider_id:
            raise ServiceAccessDenied()
        updated = ServiceQuestionRepository.update(db, question_id, dto)
        db.commit()
        return ServiceQuestionMapper.model_to_dto(updated)

    @staticmethod
    def delete(db: Session, question_id: int, user_account_id: int) -> None:
        question = ServiceQuestionRepository.get_by_id(db, question_id)
        if not question:
            raise ServiceQuestionNotFound()
        service = ServiceRepository.get_by_id(db, question.service_id)
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider or not service or provider.id != service.provider_id:
            raise ServiceAccessDenied()
        ServiceQuestionRepository.delete(db, question_id)
        db.commit()
        logger.info("Question supprimée : id=%d", question_id)

    @staticmethod
    def calculate_duration(db: Session, service_id: int, dto: DurationCalculateDTO) -> DurationResponseDTO:
        service = ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise ServiceNotFound()
        duration = service.default_duration
        for answer in dto.answers:
            question = ServiceQuestionRepository.get_by_id(db, answer.question_id)
            if not question:
                raise ServiceQuestionNotFound()
            if answer.option_index >= len(question.options):
                raise ServiceQuestionIndexError()
            duration += question.options[answer.option_index]["extra_minutes"]
        return DurationResponseDTO(duration=duration)
