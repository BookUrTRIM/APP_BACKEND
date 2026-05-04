from typing import Optional

from daos.client_dao import ClientDAO
from dtos.client.client_create_dto import ClientCreateDTO
from dtos.client.client_update_dto import ClientUpdateDTO
from mappers.client_mapper import ClientMapper
from models.client_model import ClientModel
from shared.db import get_db_session


class ClientRepository:
    @staticmethod
    def create(dto: ClientCreateDTO, user_account_id: int) -> ClientModel:
        session = get_db_session()

        dao = ClientDAO(
            user_account_id=user_account_id,
            last_name=dto.last_name,
            first_name=dto.first_name,
            phone=dto.phone,
            gender=dto.gender,
            hair_length=dto.hair_length,
            hair_type=dto.hair_type,
            history_preferences=dto.history_preferences,
        )
        session.add(dao)
        session.commit()
        session.refresh(dao)
        return ClientMapper.dao_to_model(dao)

    @staticmethod
    def update(client_id: int, dto: ClientUpdateDTO) -> Optional[ClientModel]:
        session = get_db_session()
        dao = session.get(ClientDAO, client_id)
        if not dao:
            return None

        if dto.last_name is not None:
            dao.last_name = dto.last_name
        if dto.first_name is not None:
            dao.first_name = dto.first_name
        if dto.phone is not None:
            dao.phone = dto.phone
        if dto.gender is not None:
            dao.gender = dto.gender
        if dto.hair_length is not None:
            dao.hair_length = dto.hair_length
        if dto.hair_type is not None:
            dao.hair_type = dto.hair_type
        if dto.history_preferences is not None:
            dao.history_preferences = dto.history_preferences

        session.commit()
        session.refresh(dao)
        return ClientMapper.dao_to_model(dao)

    @staticmethod
    def get_by_id(client_id: int) -> Optional[ClientModel]:
        session = get_db_session()
        dao = session.get(ClientDAO, client_id)
        return ClientMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def get_by_user_account_id(user_account_id: int) -> Optional[ClientModel]:
        session = get_db_session()
        dao = session.query(ClientDAO).where(ClientDAO.user_account_id == user_account_id).first()
        return ClientMapper.dao_to_model(dao) if dao else None
