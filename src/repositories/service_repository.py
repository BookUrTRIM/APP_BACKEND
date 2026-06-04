from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from daos.service_dao import ServiceDAO
from dtos.service.service_create_dto import ServiceCreateDTO
from dtos.service.service_update_dto import ServiceUpdateDTO
from mappers.service_mapper import ServiceMapper
from models.service_model import ServiceModel


class ServiceRepository:
    @staticmethod
    def create(db: Session, dto: ServiceCreateDTO, provider_id: int) -> ServiceModel:
        dao = ServiceDAO(
            provider_id=provider_id,
            name=dto.name,
            description=dto.description,
            default_duration=dto.default_duration,
            base_price=dto.base_price,
            deposit_amount=dto.deposit_amount,
        )
        db.add(dao)
        db.flush()
        db.refresh(dao)
        return ServiceMapper.dao_to_model(dao)

    @staticmethod
    def update(db: Session, service_id: int, dto: ServiceUpdateDTO) -> Optional[ServiceModel]:
        dao = db.get(ServiceDAO, service_id)
        if not dao:
            return None

        if dto.name is not None:
            dao.name = dto.name
        if dto.description is not None:
            dao.description = dto.description
        if dto.default_duration is not None:
            dao.default_duration = dto.default_duration
        if dto.base_price is not None:
            dao.base_price = dto.base_price
        if dto.deposit_amount is not None:
            dao.deposit_amount = dto.deposit_amount

        db.flush()
        db.refresh(dao)
        return ServiceMapper.dao_to_model(dao)

    @staticmethod
    def delete(db: Session, service_id: int) -> bool:
        dao = db.get(ServiceDAO, service_id)
        if not dao:
            return False
        db.delete(dao)
        db.flush()
        return True

    @staticmethod
    def get_by_id(db: Session, service_id: int) -> Optional[ServiceModel]:
        dao = db.get(ServiceDAO, service_id)
        return ServiceMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def list_by_provider(db: Session, provider_id: int, page: int = 1, limit: int = 20) -> Tuple[List[ServiceModel], int]:
        query = db.query(ServiceDAO).where(ServiceDAO.provider_id == provider_id)
        total = query.count()
        rows = query.order_by(ServiceDAO.name).limit(limit).offset((page - 1) * limit).all()
        return [ServiceMapper.dao_to_model(row) for row in rows], total
