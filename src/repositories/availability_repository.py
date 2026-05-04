from datetime import date
from typing import List, Optional

from daos.availability_dao import AvailabilityDAO
from dtos.availability.availability_create_dto import AvailabilityCreateDTO
from dtos.availability.availability_update_dto import AvailabilityUpdateDTO
from mappers.availability_mapper import AvailabilityMapper
from models.availability_model import AvailabilityModel
from shared.db import get_db_session


class AvailabilityRepository:
    @staticmethod
    def create(dto: AvailabilityCreateDTO, provider_id: int) -> AvailabilityModel:
        session = get_db_session()

        dao = AvailabilityDAO(
            provider_id=provider_id,
            day_date=dto.day_date,
            start_time=dto.start_time,
            end_time=dto.end_time,
            slot_type=dto.slot_type,
        )
        session.add(dao)
        session.commit()
        session.refresh(dao)
        return AvailabilityMapper.dao_to_model(dao)

    @staticmethod
    def update(availability_id: int, dto: AvailabilityUpdateDTO) -> Optional[AvailabilityModel]:
        session = get_db_session()
        dao = session.get(AvailabilityDAO, availability_id)
        if not dao:
            return None

        if dto.day_date is not None:
            dao.day_date = dto.day_date
        if dto.start_time is not None:
            dao.start_time = dto.start_time
        if dto.end_time is not None:
            dao.end_time = dto.end_time
        if dto.slot_type is not None:
            dao.slot_type = dto.slot_type

        session.commit()
        session.refresh(dao)
        return AvailabilityMapper.dao_to_model(dao)

    @staticmethod
    def delete(availability_id: int) -> bool:
        session = get_db_session()
        dao = session.get(AvailabilityDAO, availability_id)
        if not dao:
            return False

        session.delete(dao)
        session.commit()
        return True

    @staticmethod
    def get_by_id(availability_id: int) -> Optional[AvailabilityModel]:
        session = get_db_session()
        dao = session.get(AvailabilityDAO, availability_id)
        return AvailabilityMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def list_by_provider(provider_id: int, day_date: Optional[date] = None) -> List[AvailabilityModel]:
        session = get_db_session()
        query = session.query(AvailabilityDAO).where(AvailabilityDAO.provider_id == provider_id)

        if day_date is not None:
            query = query.where(AvailabilityDAO.day_date == day_date)

        rows = query.order_by(AvailabilityDAO.day_date, AvailabilityDAO.start_time).all()
        return [AvailabilityMapper.dao_to_model(row) for row in rows]
