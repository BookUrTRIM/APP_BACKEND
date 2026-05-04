import logging
from typing import List, Tuple

from dtos.provider.provider_create_dto import ProviderCreateDTO
from dtos.provider.provider_response_dto import ProviderResponseDTO
from dtos.provider.provider_update_dto import ProviderUpdateDTO
from exceptions.provider_exceptions import ProviderAccessDenied, ProviderAlreadyExists, ProviderNotFound
from mappers.provider_mapper import ProviderMapper
from repositories.provider_repository import ProviderRepository

logger = logging.getLogger(__name__)


class ProviderService:
    @staticmethod
    def create(user_account_id: int, dto: ProviderCreateDTO) -> ProviderResponseDTO:
        if ProviderRepository.get_by_user_account_id(user_account_id):
            raise ProviderAlreadyExists()

        provider = ProviderRepository.create(dto, user_account_id)
        logger.info("Profil prestataire créé : id=%d user_account_id=%d", provider.id, provider.user_account_id)
        return ProviderMapper.model_to_dto(provider)

    @staticmethod
    def update(provider_id: int, current_user_account_id: int, dto: ProviderUpdateDTO) -> ProviderResponseDTO:
        provider = ProviderRepository.get_by_id(provider_id)
        if not provider:
            raise ProviderNotFound()
        if provider.user_account_id != current_user_account_id:
            raise ProviderAccessDenied()

        updated = ProviderRepository.update(provider_id, dto)
        return ProviderMapper.model_to_dto(updated)

    @staticmethod
    def get(provider_id: int) -> ProviderResponseDTO:
        provider = ProviderRepository.get_by_id(provider_id)
        if not provider:
            raise ProviderNotFound()
        return ProviderMapper.model_to_dto(provider)

    @staticmethod
    def get_me(user_account_id: int) -> ProviderResponseDTO:
        provider = ProviderRepository.get_by_user_account_id(user_account_id)
        if not provider:
            raise ProviderNotFound()
        return ProviderMapper.model_to_dto(provider)

    @staticmethod
    def list(page: int = 1, limit: int = 20) -> Tuple[List[ProviderResponseDTO], int]:
        providers, total = ProviderRepository.list(page=page, limit=limit)
        return [ProviderMapper.model_to_dto(p) for p in providers], total
