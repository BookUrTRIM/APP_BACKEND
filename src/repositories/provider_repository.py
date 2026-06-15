from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from daos.provider_dao import ProviderDAO
from dtos.provider.provider_create_dto import ProviderCreateDTO
from dtos.provider.provider_update_dto import ProviderUpdateDTO
from mappers.provider_mapper import ProviderMapper
from models.provider_model import ProviderModel


class ProviderRepository:
    @staticmethod
    def create(db: Session, dto: ProviderCreateDTO, user_account_id: int) -> ProviderModel:
        dao = ProviderDAO(
            user_account_id=user_account_id,
            last_name=dto.last_name,
            first_name=dto.first_name,
            phone=dto.phone,
            business_name=dto.business_name,
            address=dto.address,
        )
        db.add(dao)
        db.flush()
        db.refresh(dao)
        return ProviderMapper.dao_to_model(dao)

    @staticmethod
    def update(db: Session, provider_id: int, dto: ProviderUpdateDTO) -> Optional[ProviderModel]:
        dao = db.get(ProviderDAO, provider_id)
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
        if dto.is_single_tenant is not None:
            dao.is_single_tenant = dto.is_single_tenant

        db.flush()
        db.refresh(dao)
        return ProviderMapper.dao_to_model(dao)

    @staticmethod
    def get_by_id(db: Session, provider_id: int) -> Optional[ProviderModel]:
        dao = db.get(ProviderDAO, provider_id)
        return ProviderMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def get_by_user_account_id(db: Session, user_account_id: int) -> Optional[ProviderModel]:
        dao = db.query(ProviderDAO).where(ProviderDAO.user_account_id == user_account_id).first()
        return ProviderMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def set_stripe_account(db: Session, provider_id: int, stripe_account_id: str) -> Optional[ProviderModel]:
        dao = db.get(ProviderDAO, provider_id)
        if not dao:
            return None
        dao.stripe_account_id = stripe_account_id
        db.flush()
        db.refresh(dao)
        return ProviderMapper.dao_to_model(dao)

    @staticmethod
    def list(db: Session, page: int = 1, limit: int = 20) -> Tuple[List[ProviderModel], int]:
        query = db.query(ProviderDAO)
        total = query.count()
        rows = query.order_by(ProviderDAO.last_name).limit(limit).offset((page - 1) * limit).all()
        return [ProviderMapper.dao_to_model(row) for row in rows], total
