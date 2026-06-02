from typing import List, Optional, Tuple

from daos.provider_dao import ProviderDAO
from dtos.provider.provider_create_dto import ProviderCreateDTO
from dtos.provider.provider_update_dto import ProviderUpdateDTO
from mappers.provider_mapper import ProviderMapper
from models.provider_model import ProviderModel
from shared.db import get_db_session


class ProviderRepository:
    @staticmethod
    def create(dto: ProviderCreateDTO, user_account_id: int) -> ProviderModel:
        session = get_db_session()

        dao = ProviderDAO(
            user_account_id=user_account_id,
            last_name=dto.last_name,
            first_name=dto.first_name,
            phone=dto.phone,
            business_name=dto.business_name,
            address=dto.address,
        )
        session.add(dao)
        session.commit()
        session.refresh(dao)
        return ProviderMapper.dao_to_model(dao)

    @staticmethod
    def update(provider_id: int, dto: ProviderUpdateDTO) -> Optional[ProviderModel]:
        session = get_db_session()
        dao = session.get(ProviderDAO, provider_id)
        if not dao:
            return None

        if dto.last_name is not None:
            dao.last_name = dto.last_name
        if dto.first_name is not None:
            dao.first_name = dto.first_name
        if dto.phone is not None:
            dao.phone = dto.phone
        if dto.business_name is not None:
            dao.business_name = dto.business_name
        if dto.address is not None:
            dao.address = dto.address

        session.commit()
        session.refresh(dao)
        return ProviderMapper.dao_to_model(dao)

    @staticmethod
    def get_by_id(provider_id: int) -> Optional[ProviderModel]:
        session = get_db_session()
        dao = session.get(ProviderDAO, provider_id)
        return ProviderMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def get_by_user_account_id(user_account_id: int) -> Optional[ProviderModel]:
        session = get_db_session()
        dao = session.query(ProviderDAO).where(ProviderDAO.user_account_id == user_account_id).first()
        return ProviderMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def set_stripe_account(provider_id: int, stripe_account_id: str) -> Optional[ProviderModel]:
        session = get_db_session()
        dao = session.get(ProviderDAO, provider_id)
        if not dao:
            return None
        dao.stripe_account_id = stripe_account_id
        session.commit()
        session.refresh(dao)
        return ProviderMapper.dao_to_model(dao)

    @staticmethod
    def list(page: int = 1, limit: int = 20) -> Tuple[List[ProviderModel], int]:
        session = get_db_session()
        query = session.query(ProviderDAO)

        total = query.count()
        rows = query.order_by(ProviderDAO.last_name).limit(limit).offset((page - 1) * limit).all()
        return [ProviderMapper.dao_to_model(row) for row in rows], total
