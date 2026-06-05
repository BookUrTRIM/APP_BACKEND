from datetime import datetime
from typing import List, Optional, Tuple

import sqlalchemy as sa
from sqlalchemy.orm import Session

from daos.appointment_dao import AppointmentDAO
from daos.appointment_service_dao import AppointmentServiceDAO
from daos.service_dao import ServiceDAO
from dtos.appointment.appointment_create_dto import AppointmentCreateDTO
from dtos.appointment.appointment_update_dto import AppointmentUpdateDTO
from enums.appointment_enum import AppointmentStatus
from mappers.appointment_mapper import AppointmentMapper
from models.appointment_model import AppointmentModel


class AppointmentRepository:
    @staticmethod
    def create(db: Session, dto: AppointmentCreateDTO, client_id: int) -> AppointmentModel:
        dao = AppointmentDAO(
            client_id=client_id,
            provider_id=dto.provider_id,
            start_at=dto.start_at,
            end_at=dto.end_at,
            specific_request=dto.specific_request,
            answers=[a.model_dump() for a in dto.answers] if dto.answers else None,
        )
        db.add(dao)
        db.flush()
        db.refresh(dao)

        if dto.service_id:
            service = db.get(ServiceDAO, dto.service_id)
            if service:
                db.add(AppointmentServiceDAO(
                    appointment_id=dao.id,
                    service_id=dto.service_id,
                    billed_price=service.base_price,
                ))
                if service.deposit_amount is not None:
                    dao.deposit_amount = service.deposit_amount
                db.flush()
                db.refresh(dao)

        model = AppointmentMapper.dao_to_model(dao)
        model.service_name, model.service_base_price = AppointmentRepository._get_service_info(db, dao.id)
        return model

    @staticmethod
    def update(db: Session, appointment_id: int, dto: AppointmentUpdateDTO) -> Optional[AppointmentModel]:
        dao = db.get(AppointmentDAO, appointment_id)
        if not dao:
            return None

        if dto.status is not None:
            dao.status = dto.status
        if dto.products_used is not None:
            dao.products_used = dto.products_used
        if dto.specific_request is not None:
            dao.specific_request = dto.specific_request

        db.flush()
        db.refresh(dao)
        model = AppointmentMapper.dao_to_model(dao)
        model.service_name, model.service_base_price = AppointmentRepository._get_service_info(db, appointment_id)
        return model

    @staticmethod
    def delete(db: Session, appointment_id: int) -> bool:
        dao = db.get(AppointmentDAO, appointment_id)
        if not dao:
            return False
        db.delete(dao)
        db.flush()
        return True

    @staticmethod
    def count_pending_by_client(db: Session, client_id: int) -> int:
        return (
            db.query(AppointmentDAO)
            .where(AppointmentDAO.client_id == client_id)
            .where(AppointmentDAO.status == AppointmentStatus.PENDING.value)
            .count()
        )

    @staticmethod
    def expire_old_pending(db: Session, threshold: datetime) -> int:
        result = db.execute(
            sa.update(AppointmentDAO)
            .where(AppointmentDAO.status == AppointmentStatus.PENDING.value)
            .where(AppointmentDAO.created_at < threshold)
            .values(status=AppointmentStatus.EXPIRED.value)
        )
        return result.rowcount

    @staticmethod
    def update_status(db: Session, appointment_id: int, status: AppointmentStatus) -> Optional[AppointmentModel]:
        dao = db.get(AppointmentDAO, appointment_id)
        if not dao:
            return None
        dao.status = status
        db.flush()
        db.refresh(dao)
        model = AppointmentMapper.dao_to_model(dao)
        model.service_name, model.service_base_price = AppointmentRepository._get_service_info(db, appointment_id)
        return model

    @staticmethod
    def has_conflict(db: Session, provider_id: int, start_at: datetime, end_at: datetime) -> bool:
        count = (
            db.query(AppointmentDAO)
            .where(AppointmentDAO.provider_id == provider_id)
            .where(AppointmentDAO.status.in_([
                AppointmentStatus.PENDING.value,
                AppointmentStatus.CONFIRMED.value,
            ]))
            .where(AppointmentDAO.start_at < end_at)
            .where(AppointmentDAO.end_at > start_at)
            .count()
        )
        return count > 0

    @staticmethod
    def _get_service_info(db: Session, appointment_id: int) -> tuple:
        result = (
            db.query(ServiceDAO.name, ServiceDAO.base_price)
            .join(AppointmentServiceDAO, AppointmentServiceDAO.service_id == ServiceDAO.id)
            .where(AppointmentServiceDAO.appointment_id == appointment_id)
            .first()
        )
        if result:
            return result[0], float(result[1])
        return None, None

    @staticmethod
    def get_by_id(db: Session, appointment_id: int) -> Optional[AppointmentModel]:
        dao = db.get(AppointmentDAO, appointment_id)
        if not dao:
            return None
        model = AppointmentMapper.dao_to_model(dao)
        model.service_name, model.service_base_price = AppointmentRepository._get_service_info(db, appointment_id)
        return model

    @staticmethod
    def list_by_client(
        db: Session,
        client_id: int,
        status: Optional[AppointmentStatus] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[AppointmentModel], int]:
        query = db.query(AppointmentDAO).where(AppointmentDAO.client_id == client_id)
        if status is not None:
            query = query.where(AppointmentDAO.status == status)
        total = query.count()
        rows = query.order_by(AppointmentDAO.start_at.desc()).limit(limit).offset((page - 1) * limit).all()
        models = []
        for row in rows:
            model = AppointmentMapper.dao_to_model(row)
            model.service_name, model.service_base_price = AppointmentRepository._get_service_info(db, row.id)
            models.append(model)
        return models, total

    @staticmethod
    def list_by_provider(
        db: Session,
        provider_id: int,
        status: Optional[AppointmentStatus] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[AppointmentModel], int]:
        query = db.query(AppointmentDAO).where(AppointmentDAO.provider_id == provider_id)
        if status is not None:
            query = query.where(AppointmentDAO.status == status)
        total = query.count()
        rows = query.order_by(AppointmentDAO.start_at.desc()).limit(limit).offset((page - 1) * limit).all()
        models = []
        for row in rows:
            model = AppointmentMapper.dao_to_model(row)
            model.service_name, model.service_base_price = AppointmentRepository._get_service_info(db, row.id)
            models.append(model)
        return models, total
