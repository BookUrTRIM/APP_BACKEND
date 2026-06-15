import logging
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

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
    def create(db: Session, user_account_id: int, dto: AvailabilityCreateDTO) -> AvailabilityResponseDTO:
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider:
            raise ProviderNotFound()
        availability = AvailabilityRepository.create(db, dto, provider.id)
        db.commit()
        logger.info("Disponibilité créée : id=%d provider_id=%d", availability.id, availability.provider_id)
        return AvailabilityMapper.model_to_dto(availability)

    @staticmethod
    def create_bulk(db: Session, user_account_id: int, dtos: list[AvailabilityCreateDTO]) -> list[AvailabilityResponseDTO]:
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider:
            raise ProviderNotFound()
        availabilities = AvailabilityRepository.create_bulk(db, dtos, provider.id)
        db.commit()
        logger.info("Création en masse : %d créneaux générés pour provider_id=%d", len(availabilities), provider.id)
        return [AvailabilityMapper.model_to_dto(a) for a in availabilities]

    @staticmethod
    def update(db: Session, availability_id: int, user_account_id: int, dto: AvailabilityUpdateDTO) -> AvailabilityResponseDTO:
        availability = AvailabilityRepository.get_by_id(db, availability_id)
        if not availability:
            raise AvailabilityNotFound()
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider or provider.id != availability.provider_id:
            raise AvailabilityAccessDenied()
        updated = AvailabilityRepository.update(db, availability_id, dto)
        db.commit()
        return AvailabilityMapper.model_to_dto(updated)

    @staticmethod
    def delete(db: Session, availability_id: int, user_account_id: int) -> None:
        availability = AvailabilityRepository.get_by_id(db, availability_id)
        if not availability:
            raise AvailabilityNotFound()
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider or provider.id != availability.provider_id:
            raise AvailabilityAccessDenied()
        AvailabilityRepository.delete(db, availability_id)
        db.commit()

    @staticmethod
    def list_by_provider(db: Session, provider_id: int, day_date: Optional[date] = None) -> List[AvailabilityResponseDTO]:
        slots = AvailabilityRepository.list_by_provider(db, provider_id, day_date=day_date)
        return [AvailabilityMapper.model_to_dto(s) for s in slots]
