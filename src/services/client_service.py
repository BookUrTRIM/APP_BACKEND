import logging
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from dtos.client.client_create_dto import ClientCreateDTO
from dtos.client.client_response_dto import ClientResponseDTO
from dtos.client.client_update_dto import ClientUpdateDTO
from dtos.client.hair_profile_response_dto import HairProfileResponseDTO
from dtos.client.hair_profile_upsert_dto import HairProfileUpsertDTO
from exceptions.client_exceptions import ClientAccessDenied, ClientAlreadyExists, ClientNotFound
from mappers.client_hair_profile_mapper import ClientHairProfileMapper
from mappers.client_mapper import ClientMapper
from repositories.client_hair_profile_repository import ClientHairProfileRepository
from repositories.client_repository import ClientRepository

logger = logging.getLogger(__name__)


class ClientService:
    @staticmethod
    def create(db: Session, user_account_id: int, dto: ClientCreateDTO) -> ClientResponseDTO:
        if ClientRepository.get_by_user_account_id(db, user_account_id):
            raise ClientAlreadyExists()
        client = ClientRepository.create(db, dto, user_account_id)
        db.commit()
        logger.info("Profil client créé : id=%d user_account_id=%d", client.id, client.user_account_id)
        return ClientMapper.model_to_dto(client)

    @staticmethod
    def update(db: Session, client_id: int, current_user_account_id: int, dto: ClientUpdateDTO) -> ClientResponseDTO:
        client = ClientRepository.get_by_id(db, client_id)
        if not client:
            raise ClientNotFound()
        if client.user_account_id != current_user_account_id:
            raise ClientAccessDenied()
        updated = ClientRepository.update(db, client_id, dto)
        db.commit()
        return ClientMapper.model_to_dto(updated)

    @staticmethod
    def get(db: Session, client_id: int) -> ClientResponseDTO:
        client = ClientRepository.get_by_id(db, client_id)
        if not client:
            raise ClientNotFound()
        return ClientMapper.model_to_dto(client)

    @staticmethod
    def get_me(db: Session, user_account_id: int) -> ClientResponseDTO:
        client = ClientRepository.get_by_user_account_id(db, user_account_id)
        if not client:
            raise ClientNotFound()
        return ClientMapper.model_to_dto(client)

    @staticmethod
    def get_hair_profile(db: Session, user_account_id: int) -> Optional[HairProfileResponseDTO]:
        client = ClientRepository.get_by_user_account_id(db, user_account_id)
        if not client:
            raise ClientNotFound()
        profile = ClientHairProfileRepository.get_by_client(db, client.id)
        return ClientHairProfileMapper.model_to_dto(profile) if profile else None

    @staticmethod
    def upsert_hair_profile(db: Session, user_account_id: int, dto: HairProfileUpsertDTO) -> HairProfileResponseDTO:
        client = ClientRepository.get_by_user_account_id(db, user_account_id)
        if not client:
            raise ClientNotFound()
        profile = ClientHairProfileRepository.upsert(db, client.id, dto)
        db.commit()
        logger.info("Profil capillaire mis à jour : client_id=%d", client.id)
        return ClientHairProfileMapper.model_to_dto(profile)
