from typing import Optional

from sqlalchemy.orm import Session

from daos.client_hair_profile_dao import ClientHairProfileDAO
from dtos.client.hair_profile_upsert_dto import HairProfileUpsertDTO
from mappers.client_hair_profile_mapper import ClientHairProfileMapper
from models.client_hair_profile_model import ClientHairProfileModel


class ClientHairProfileRepository:
    @staticmethod
    def get_by_client(db: Session, client_id: int) -> Optional[ClientHairProfileModel]:
        dao = (
            db.query(ClientHairProfileDAO)
            .where(ClientHairProfileDAO.client_id == client_id)
            .first()
        )
        return ClientHairProfileMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def upsert(db: Session, client_id: int, dto: HairProfileUpsertDTO) -> ClientHairProfileModel:
        dao = (
            db.query(ClientHairProfileDAO)
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
            db.add(dao)

        db.flush()
        db.refresh(dao)
        return ClientHairProfileMapper.dao_to_model(dao)
