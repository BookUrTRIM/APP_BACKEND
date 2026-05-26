from datetime import datetime
from typing import List, Optional, Tuple

import sqlalchemy as sa

from daos.appointment_dao import AppointmentDAO
from dtos.appointment.appointment_create_dto import AppointmentCreateDTO
from dtos.appointment.appointment_update_dto import AppointmentUpdateDTO
from enums.appointment_enum import AppointmentStatus
from mappers.appointment_mapper import AppointmentMapper
from models.appointment_model import AppointmentModel
from shared.db import get_db_session


class AppointmentRepository:
    @staticmethod
    def create(dto: AppointmentCreateDTO, client_id: int) -> AppointmentModel:
        session = get_db_session()

        dao = AppointmentDAO(
            client_id=client_id,
            provider_id=dto.provider_id,
            start_at=dto.start_at,
            end_at=dto.end_at,
            specific_request=dto.specific_request,
        )
        session.add(dao)
        session.commit()
        session.refresh(dao)
        return AppointmentMapper.dao_to_model(dao)

    @staticmethod
    def update(appointment_id: int, dto: AppointmentUpdateDTO) -> Optional[AppointmentModel]:
        session = get_db_session()
        dao = session.get(AppointmentDAO, appointment_id)
        if not dao:
            return None

        if dto.status is not None:
            dao.status = dto.status
        if dto.products_used is not None:
            dao.products_used = dto.products_used
        if dto.specific_request is not None:
            dao.specific_request = dto.specific_request

        session.commit()
        session.refresh(dao)
        return AppointmentMapper.dao_to_model(dao)

    @staticmethod
    def delete(appointment_id: int) -> bool:
        session = get_db_session()
        dao = session.get(AppointmentDAO, appointment_id)
        if not dao:
            return False

        session.delete(dao)
        session.commit()
        return True

    @staticmethod
    def count_pending_by_client(client_id: int) -> int:
        session = get_db_session()
        return (
            session.query(AppointmentDAO)
            .where(AppointmentDAO.client_id == client_id)
            .where(AppointmentDAO.status == AppointmentStatus.PENDING)
            .count()
        )

    @staticmethod
    def expire_old_pending(threshold: datetime) -> int:
        session = get_db_session()
        result = session.execute(
            sa.update(AppointmentDAO)
            .where(AppointmentDAO.status == AppointmentStatus.PENDING)
            .where(AppointmentDAO.created_at < threshold)
            .values(status=AppointmentStatus.EXPIRED)
        )
        session.commit()
        return result.rowcount

    @staticmethod
    def update_status(appointment_id: int, status: AppointmentStatus) -> Optional[AppointmentModel]:
        session = get_db_session()
        dao = session.get(AppointmentDAO, appointment_id)
        if not dao:
            return None
        dao.status = status
        session.commit()
        session.refresh(dao)
        return AppointmentMapper.dao_to_model(dao)

    @staticmethod
    def get_by_id(appointment_id: int) -> Optional[AppointmentModel]:
        session = get_db_session()
        dao = session.get(AppointmentDAO, appointment_id)
        return AppointmentMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def list_by_client(
        client_id: int,
        status: Optional[AppointmentStatus] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[AppointmentModel], int]:
        session = get_db_session()
        query = session.query(AppointmentDAO).where(AppointmentDAO.client_id == client_id)

        if status is not None:
            query = query.where(AppointmentDAO.status == status)

        total = query.count()
        rows = query.order_by(AppointmentDAO.start_at.desc()).limit(limit).offset((page - 1) * limit).all()
        return [AppointmentMapper.dao_to_model(row) for row in rows], total

    @staticmethod
    def list_by_provider(
        provider_id: int,
        status: Optional[AppointmentStatus] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[AppointmentModel], int]:
        session = get_db_session()
        query = session.query(AppointmentDAO).where(AppointmentDAO.provider_id == provider_id)

        if status is not None:
            query = query.where(AppointmentDAO.status == status)

        total = query.count()
        rows = query.order_by(AppointmentDAO.start_at.desc()).limit(limit).offset((page - 1) * limit).all()
        return [AppointmentMapper.dao_to_model(row) for row in rows], total
