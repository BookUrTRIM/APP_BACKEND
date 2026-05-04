from typing import List, Optional

from daos.appointment_service_dao import AppointmentServiceDAO
from dtos.appointment.appointment_service_create_dto import AppointmentServiceCreateDTO
from mappers.appointment_service_mapper import AppointmentServiceMapper
from models.appointment_service_model import AppointmentServiceModel
from shared.db import get_db_session


class AppointmentServiceRepository:
    @staticmethod
    def add(appointment_id: int, dto: AppointmentServiceCreateDTO) -> AppointmentServiceModel:
        session = get_db_session()

        dao = AppointmentServiceDAO(
            appointment_id=appointment_id,
            service_id=dto.service_id,
            adjusted_duration=dto.adjusted_duration,
            billed_price=dto.billed_price,
        )
        session.add(dao)
        session.commit()
        return AppointmentServiceMapper.dao_to_model(dao)

    @staticmethod
    def remove(appointment_id: int, service_id: int) -> bool:
        session = get_db_session()
        dao = session.get(AppointmentServiceDAO, {"appointment_id": appointment_id, "service_id": service_id})
        if not dao:
            return False

        session.delete(dao)
        session.commit()
        return True

    @staticmethod
    def get(appointment_id: int, service_id: int) -> Optional[AppointmentServiceModel]:
        session = get_db_session()
        dao = session.get(AppointmentServiceDAO, {"appointment_id": appointment_id, "service_id": service_id})
        return AppointmentServiceMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def list_by_appointment(appointment_id: int) -> List[AppointmentServiceModel]:
        session = get_db_session()
        rows = (
            session.query(AppointmentServiceDAO)
            .where(AppointmentServiceDAO.appointment_id == appointment_id)
            .all()
        )
        return [AppointmentServiceMapper.dao_to_model(row) for row in rows]
