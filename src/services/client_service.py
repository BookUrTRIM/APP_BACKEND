import logging
from typing import List, Tuple

from dtos.client.client_create_dto import ClientCreateDTO
from dtos.client.client_response_dto import ClientResponseDTO
from dtos.client.client_update_dto import ClientUpdateDTO
from exceptions.client_exceptions import ClientAccessDenied, ClientAlreadyExists, ClientNotFound
from mappers.client_mapper import ClientMapper
from repositories.client_repository import ClientRepository

logger = logging.getLogger(__name__)


class ClientService:
    @staticmethod
    def create(user_account_id: int, dto: ClientCreateDTO) -> ClientResponseDTO:
        if ClientRepository.get_by_user_account_id(user_account_id):
            raise ClientAlreadyExists()

        client = ClientRepository.create(dto, user_account_id)
        logger.info("Profil client créé : id=%d user_account_id=%d", client.id, client.user_account_id)
        return ClientMapper.model_to_dto(client)

    @staticmethod
    def update(client_id: int, current_user_account_id: int, dto: ClientUpdateDTO) -> ClientResponseDTO:
        client = ClientRepository.get_by_id(client_id)
        if not client:
            raise ClientNotFound()
        if client.user_account_id != current_user_account_id:
            raise ClientAccessDenied()

        updated = ClientRepository.update(client_id, dto)
        return ClientMapper.model_to_dto(updated)

    @staticmethod
    def get(client_id: int) -> ClientResponseDTO:
        client = ClientRepository.get_by_id(client_id)
        if not client:
            raise ClientNotFound()
        return ClientMapper.model_to_dto(client)

    @staticmethod
    def get_me(user_account_id: int) -> ClientResponseDTO:
        client = ClientRepository.get_by_user_account_id(user_account_id)
        if not client:
            raise ClientNotFound()
        return ClientMapper.model_to_dto(client)
