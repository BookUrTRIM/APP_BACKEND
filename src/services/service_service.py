import logging
from typing import List, Tuple

from sqlalchemy.orm import Session

from dtos.service.service_create_dto import ServiceCreateDTO
from dtos.service.service_response_dto import ServiceResponseDTO
from dtos.service.service_update_dto import ServiceUpdateDTO
from exceptions.provider_exceptions import ProviderNotFound
from exceptions.service_exceptions import ServiceAccessDenied, ServiceNotFound
from mappers.service_mapper import ServiceMapper
from repositories.provider_repository import ProviderRepository
from repositories.service_repository import ServiceRepository

logger = logging.getLogger(__name__)


class ServiceService:
    @staticmethod
    def create(db: Session, user_account_id: int, dto: ServiceCreateDTO) -> ServiceResponseDTO:
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider:
            raise ProviderNotFound()
        service = ServiceRepository.create(db, dto, provider.id)
        db.commit()
        logger.info("Prestation créée : id=%d provider_id=%d", service.id, service.provider_id)
        return ServiceMapper.model_to_dto(service)

    @staticmethod
    def update(db: Session, service_id: int, user_account_id: int, dto: ServiceUpdateDTO) -> ServiceResponseDTO:
        service = ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise ServiceNotFound()
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider or provider.id != service.provider_id:
            raise ServiceAccessDenied()
        updated = ServiceRepository.update(db, service_id, dto)
        db.commit()
        return ServiceMapper.model_to_dto(updated)

    @staticmethod
    def delete(db: Session, service_id: int, user_account_id: int) -> None:
        service = ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise ServiceNotFound()
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider or provider.id != service.provider_id:
            raise ServiceAccessDenied()
        ServiceRepository.delete(db, service_id)
        db.commit()

    @staticmethod
    def get(db: Session, service_id: int) -> ServiceResponseDTO:
        service = ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise ServiceNotFound()
        return ServiceMapper.model_to_dto(service)

    @staticmethod
    def list_by_provider(db: Session, provider_id: int, page: int = 1, limit: int = 20) -> Tuple[List[ServiceResponseDTO], int]:
        services, total = ServiceRepository.list_by_provider(db, provider_id, page=page, limit=limit)
        return [ServiceMapper.model_to_dto(s) for s in services], total
