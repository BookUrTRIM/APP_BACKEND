import logging
from typing import List

from dtos.service.service_question_create_dto import ServiceQuestionCreateDTO
from dtos.service.service_question_response_dto import ServiceQuestionResponseDTO
from dtos.service.service_question_update_dto import ServiceQuestionUpdateDTO
from exceptions.provider_exceptions import ProviderNotFound
from exceptions.service_exceptions import ServiceAccessDenied, ServiceNotFound
from exceptions.service_question_exceptions import ServiceQuestionNotFound
from mappers.service_question_mapper import ServiceQuestionMapper
from repositories.provider_repository import ProviderRepository
from repositories.service_question_repository import ServiceQuestionRepository
from repositories.service_repository import ServiceRepository

logger = logging.getLogger(__name__)


class ServiceQuestionService:
    @staticmethod
    def list(service_id: int) -> List[ServiceQuestionResponseDTO]:
        if not ServiceRepository.get_by_id(service_id):
            raise ServiceNotFound()
        questions = ServiceQuestionRepository.list_by_service(service_id)
        return [ServiceQuestionMapper.model_to_dto(q) for q in questions]

    @staticmethod
    def create(service_id: int, user_account_id: int, dto: ServiceQuestionCreateDTO) -> ServiceQuestionResponseDTO:
        service = ServiceRepository.get_by_id(service_id)
        if not service:
            raise ServiceNotFound()

        provider = ProviderRepository.get_by_user_account_id(user_account_id)
        if not provider or provider.id != service.provider_id:
            raise ServiceAccessDenied()

        question = ServiceQuestionRepository.create(service_id, dto)
        logger.info("Question créée : id=%d service_id=%d", question.id, service_id)
        return ServiceQuestionMapper.model_to_dto(question)

    @staticmethod
    def update(question_id: int, user_account_id: int, dto: ServiceQuestionUpdateDTO) -> ServiceQuestionResponseDTO:
        question = ServiceQuestionRepository.get_by_id(question_id)
        if not question:
            raise ServiceQuestionNotFound()

        service = ServiceRepository.get_by_id(question.service_id)
        provider = ProviderRepository.get_by_user_account_id(user_account_id)
        if not provider or not service or provider.id != service.provider_id:
            raise ServiceAccessDenied()

        updated = ServiceQuestionRepository.update(question_id, dto)
        return ServiceQuestionMapper.model_to_dto(updated)

    @staticmethod
    def delete(question_id: int, user_account_id: int) -> None:
        question = ServiceQuestionRepository.get_by_id(question_id)
        if not question:
            raise ServiceQuestionNotFound()

        service = ServiceRepository.get_by_id(question.service_id)
        provider = ProviderRepository.get_by_user_account_id(user_account_id)
        if not provider or not service or provider.id != service.provider_id:
            raise ServiceAccessDenied()

        ServiceQuestionRepository.delete(question_id)
        logger.info("Question supprimée : id=%d", question_id)
