from typing import Optional

from daos.client_hair_profile_dao import ClientHairProfileDAO
from dtos.client.hair_profile_upsert_dto import HairProfileUpsertDTO
from mappers.client_hair_profile_mapper import ClientHairProfileMapper
from models.client_hair_profile_model import ClientHairProfileModel
from shared.db import get_db_session


class ClientHairProfileRepository:
    @staticmethod
    def get_by_client(client_id: int) -> Optional[ClientHairProfileModel]:
        session = get_db_session()
        dao = (
            session.query(ClientHairProfileDAO)
            .where(ClientHairProfileDAO.client_id == client_id)
            .first()
        )
        return ClientHairProfileMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def upsert(client_id: int, dto: HairProfileUpsertDTO) -> ClientHairProfileModel:
        session = get_db_session()
        dao = (
            session.query(ClientHairProfileDAO)
            .where(ClientHairProfileDAO.client_id == client_id)
            .first()
        )
        if dao:
            dao.hair_type   = dto.hair_type
            dao.hair_length = dto.hair_length
        else:
            dao = ClientHairProfileDAO(
                client_id=client_id,
                hair_type=dto.hair_type,
                hair_length=dto.hair_length,
            )
            session.add(dao)

        session.commit()
        session.refresh(dao)
        return ClientHairProfileMapper.dao_to_model(dao)
