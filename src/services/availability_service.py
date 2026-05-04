import logging
from datetime import date
from typing import List, Optional

from dtos.availability.availability_create_dto import AvailabilityCreateDTO
from dtos.availability.availability_response_dto import AvailabilityResponseDTO
from dtos.availability.availability_update_dto import AvailabilityUpdateDTO
from exceptions.availability_exceptions import AvailabilityAccessDenied, AvailabilityNotFound
from exceptions.provider_exceptions import ProviderNotFound
from mappers.availability_mapper import AvailabilityMapper
from repositories.availability_repository import AvailabilityRepository
from repositories.provider_repository import ProviderRepository

logger = logging.getLogger(__name__)


class AvailabilityService:
    @staticmethod
    def create(user_account_id: int, dto: AvailabilityCreateDTO) -> AvailabilityResponseDTO:
        provider = ProviderRepository.get_by_user_account_id(user_account_id)
        if not provider:
            raise ProviderNotFound()

        availability = AvailabilityRepository.create(dto, provider.id)
        logger.info("Disponibilité créée : id=%d provider_id=%d", availability.id, availability.provider_id)
        return AvailabilityMapper.model_to_dto(availability)

    @staticmethod
    def update(
        availability_id: int,
        user_account_id: int,
        dto: AvailabilityUpdateDTO,
    ) -> AvailabilityResponseDTO:
        availability = AvailabilityRepository.get_by_id(availability_id)
        if not availability:
            raise AvailabilityNotFound()

        provider = ProviderRepository.get_by_user_account_id(user_account_id)
        if not provider or provider.id != availability.provider_id:
            raise AvailabilityAccessDenied()

        updated = AvailabilityRepository.update(availability_id, dto)
        return AvailabilityMapper.model_to_dto(updated)

    @staticmethod
    def delete(availability_id: int, user_account_id: int) -> None:
        availability = AvailabilityRepository.get_by_id(availability_id)
        if not availability:
            raise AvailabilityNotFound()

        provider = ProviderRepository.get_by_user_account_id(user_account_id)
        if not provider or provider.id != availability.provider_id:
            raise AvailabilityAccessDenied()

        AvailabilityRepository.delete(availability_id)

    @staticmethod
    def list_by_provider(
        provider_id: int,
        day_date: Optional[date] = None,
    ) -> List[AvailabilityResponseDTO]:
        slots = AvailabilityRepository.list_by_provider(provider_id, day_date=day_date)
        return [AvailabilityMapper.model_to_dto(s) for s in slots]
