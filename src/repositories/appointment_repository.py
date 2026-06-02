from datetime import datetime
from typing import List, Optional, Tuple

import sqlalchemy as sa

from daos.appointment_dao import AppointmentDAO
from daos.appointment_service_dao import AppointmentServiceDAO
from daos.service_dao import ServiceDAO
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
            answers=[a.model_dump() for a in dto.answers] if dto.answers else None,
        )
        session.add(dao)
        session.commit()
        session.refresh(dao)

        if dto.service_id:
            service = session.get(ServiceDAO, dto.service_id)
            if service:
                session.add(AppointmentServiceDAO(
                    appointment_id=dao.id,
                    service_id=dto.service_id,
                    billed_price=service.base_price,
                ))
                session.commit()

        model = AppointmentMapper.dao_to_model(dao)
        model.service_name = AppointmentRepository._get_service_name(session, dao.id)
        return model

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
        model = AppointmentMapper.dao_to_model(dao)
        model.service_name = AppointmentRepository._get_service_name(session, appointment_id)
        return model

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
            .where(AppointmentDAO.status == AppointmentStatus.PENDING.value)
            .count()
        )

    @staticmethod
    def expire_old_pending(threshold: datetime) -> int:
        session = get_db_session()
        result = session.execute(
            sa.update(AppointmentDAO)
            .where(AppointmentDAO.status == AppointmentStatus.PENDING.value)
            .where(AppointmentDAO.created_at < threshold)
            .values(status=AppointmentStatus.EXPIRED.value)
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
        model = AppointmentMapper.dao_to_model(dao)
        model.service_name = AppointmentRepository._get_service_name(session, appointment_id)
        return model

    @staticmethod
    def _get_service_name(session, appointment_id: int) -> Optional[str]:
        result = (
            session.query(ServiceDAO.name)
            .join(AppointmentServiceDAO, AppointmentServiceDAO.service_id == ServiceDAO.id)
            .where(AppointmentServiceDAO.appointment_id == appointment_id)
            .first()
        )
        return result[0] if result else None

    @staticmethod
    def get_by_id(appointment_id: int) -> Optional[AppointmentModel]:
        session = get_db_session()
        dao = session.get(AppointmentDAO, appointment_id)
        if not dao:
            return None
        model = AppointmentMapper.dao_to_model(dao)
        model.service_name = AppointmentRepository._get_service_name(session, appointment_id)
        return model

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
        models = []
        for row in rows:
            model = AppointmentMapper.dao_to_model(row)
            model.service_name = AppointmentRepository._get_service_name(session, row.id)
            models.append(model)
        return models, total

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
        models = []
        for row in rows:
            model = AppointmentMapper.dao_to_model(row)
            model.service_name = AppointmentRepository._get_service_name(session, row.id)
            models.append(model)
        return models, total
