from typing import List, Optional

from sqlalchemy.orm import Session

from daos.appointment_service_dao import AppointmentServiceDAO
from dtos.appointment.appointment_service_create_dto import AppointmentServiceCreateDTO
from mappers.appointment_service_mapper import AppointmentServiceMapper
from models.appointment_service_model import AppointmentServiceModel


class AppointmentServiceRepository:
    @staticmethod
    def add(db: Session, appointment_id: int, dto: AppointmentServiceCreateDTO) -> AppointmentServiceModel:
        dao = AppointmentServiceDAO(
            appointment_id=appointment_id,
            service_id=dto.service_id,
            adjusted_duration=dto.adjusted_duration,
            billed_price=dto.billed_price,
        )
        db.add(dao)
        db.flush()
        return AppointmentServiceMapper.dao_to_model(dao)

    @staticmethod
    def remove(db: Session, appointment_id: int, service_id: int) -> bool:
        dao = db.get(AppointmentServiceDAO, {"appointment_id": appointment_id, "service_id": service_id})
        if not dao:
            return False
        db.delete(dao)
        db.flush()
        return True

    @staticmethod
    def get(db: Session, appointment_id: int, service_id: int) -> Optional[AppointmentServiceModel]:
        dao = db.get(AppointmentServiceDAO, {"appointment_id": appointment_id, "service_id": service_id})
        return AppointmentServiceMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def list_by_appointment(db: Session, appointment_id: int) -> List[AppointmentServiceModel]:
        rows = (
            db.query(AppointmentServiceDAO)
            .where(AppointmentServiceDAO.appointment_id == appointment_id)
            .all()
        )
        return [AppointmentServiceMapper.dao_to_model(row) for row in rows]
