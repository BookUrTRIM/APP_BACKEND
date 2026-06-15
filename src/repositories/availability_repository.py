from datetime import date, datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from daos.availability_dao import AvailabilityDAO
from dtos.availability.availability_create_dto import AvailabilityCreateDTO
from dtos.availability.availability_update_dto import AvailabilityUpdateDTO
from enums.availability_enum import AvailabilityType
from mappers.availability_mapper import AvailabilityMapper
from models.appointment_model import AppointmentModel
from models.availability_model import AvailabilityModel


class AvailabilityRepository:
    @staticmethod
    def create(db: Session, dto: AvailabilityCreateDTO, provider_id: int) -> AvailabilityModel:
        dao = AvailabilityDAO(
            provider_id=provider_id,
            day_date=dto.day_date,
            start_time=dto.start_time,
            end_time=dto.end_time,
            slot_type=dto.slot_type,
        )
        db.add(dao)
        db.flush()
        db.refresh(dao)
        return AvailabilityMapper.dao_to_model(dao)

    @staticmethod
    def create_bulk(db: Session, dtos: list[AvailabilityCreateDTO], provider_id: int) -> list[AvailabilityModel]:
        daos = [
            AvailabilityDAO(
                provider_id=provider_id,
                day_date=dto.day_date,
                start_time=dto.start_time,
                end_time=dto.end_time,
                slot_type=dto.slot_type,
            ) for dto in dtos
        ]
        db.add_all(daos)
        db.flush()
        for dao in daos:
            db.refresh(dao)
        return [AvailabilityMapper.dao_to_model(dao) for dao in daos]

    @staticmethod
    def update(db: Session, availability_id: int, dto: AvailabilityUpdateDTO) -> Optional[AvailabilityModel]:
        dao = db.get(AvailabilityDAO, availability_id)
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

        db.flush()
        db.refresh(dao)
        return AvailabilityMapper.dao_to_model(dao)

    @staticmethod
    def delete(db: Session, availability_id: int) -> bool:
        dao = db.get(AvailabilityDAO, availability_id)
        if not dao:
            return False
        db.delete(dao)
        db.flush()
        return True

    @staticmethod
    def get_by_id(db: Session, availability_id: int) -> Optional[AvailabilityModel]:
        dao = db.get(AvailabilityDAO, availability_id)
        return AvailabilityMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def create_booked(db: Session, appointment: AppointmentModel) -> None:
        dao = AvailabilityDAO(
            provider_id=appointment.provider_id,
            day_date=appointment.start_at.date(),
            start_time=appointment.start_at.time(),
            end_time=appointment.end_at.time(),
            slot_type=AvailabilityType.BOOKED,
        )
        db.add(dao)
        db.flush()

    @staticmethod
    def delete_booked(db: Session, provider_id: int, start_at: datetime) -> None:
        dao = (
            db.query(AvailabilityDAO)
            .where(AvailabilityDAO.provider_id == provider_id)
            .where(AvailabilityDAO.day_date == start_at.date())
            .where(AvailabilityDAO.start_time == start_at.time())
            .where(AvailabilityDAO.slot_type == AvailabilityType.BOOKED.value)
            .first()
        )
        if dao:
            db.delete(dao)
            db.flush()

    @staticmethod
    def list_by_provider(db: Session, provider_id: int, day_date: Optional[date] = None) -> List[AvailabilityModel]:
        query = db.query(AvailabilityDAO).where(AvailabilityDAO.provider_id == provider_id)
        if day_date is not None:
            query = query.where(AvailabilityDAO.day_date == day_date)
        rows = query.order_by(AvailabilityDAO.day_date, AvailabilityDAO.start_time).all()
        return [AvailabilityMapper.dao_to_model(row) for row in rows]
