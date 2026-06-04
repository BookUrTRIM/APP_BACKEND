from datetime import datetime, timezone
from typing import Any, List, Optional

from sqlalchemy.orm import Session

from daos.payment_dao import PaymentDAO
from dtos.payment.payment_create_dto import PaymentCreateDTO
from enums.payment_enum import PaymentStatus
from mappers.payment_mapper import PaymentMapper
from models.payment_model import PaymentModel


class PaymentRepository:
    @staticmethod
    def create(db: Session, dto: PaymentCreateDTO) -> PaymentModel:
        dao = PaymentDAO(
            appointment_id=dto.appointment_id,
            amount=dto.amount,
            currency=dto.currency,
            payment_type=dto.payment_type,
        )
        db.add(dao)
        db.flush()
        db.refresh(dao)
        return PaymentMapper.dao_to_model(dao)

    @staticmethod
    def confirm(
        db: Session,
        stripe_payment_intent_id: str,
        stripe_charge_id: str,
        metadata: Optional[dict[str, Any]] = None,
        receipt_url: Optional[str] = None,
    ) -> Optional[PaymentModel]:
        dao = (
            db.query(PaymentDAO)
            .where(PaymentDAO.stripe_payment_intent_id == stripe_payment_intent_id)
            .first()
        )
        if not dao:
            return None

        dao.status = PaymentStatus.VALIDATED
        dao.stripe_charge_id = stripe_charge_id
        dao.stripe_metadata = metadata
        dao.paid_at = datetime.now(timezone.utc)
        dao.stripe_receipt_url = receipt_url

        db.flush()
        db.refresh(dao)
        return PaymentMapper.dao_to_model(dao)

    @staticmethod
    def refund(db: Session, stripe_charge_id: str) -> Optional[PaymentModel]:
        dao = (
            db.query(PaymentDAO)
            .where(PaymentDAO.stripe_charge_id == stripe_charge_id)
            .first()
        )
        if not dao:
            return None
        dao.status = PaymentStatus.REFUNDED
        db.flush()
        db.refresh(dao)
        return PaymentMapper.dao_to_model(dao)

    @staticmethod
    def fail(db: Session, stripe_payment_intent_id: str) -> Optional[PaymentModel]:
        dao = (
            db.query(PaymentDAO)
            .where(PaymentDAO.stripe_payment_intent_id == stripe_payment_intent_id)
            .first()
        )
        if not dao:
            return None
        dao.status = PaymentStatus.FAILED
        db.flush()
        db.refresh(dao)
        return PaymentMapper.dao_to_model(dao)

    @staticmethod
    def set_stripe_intent(db: Session, payment_id: int, stripe_payment_intent_id: str) -> Optional[PaymentModel]:
        dao = db.get(PaymentDAO, payment_id)
        if not dao:
            return None
        dao.stripe_payment_intent_id = stripe_payment_intent_id
        db.flush()
        db.refresh(dao)
        return PaymentMapper.dao_to_model(dao)

    @staticmethod
    def get_by_id(db: Session, payment_id: int) -> Optional[PaymentModel]:
        dao = db.get(PaymentDAO, payment_id)
        return PaymentMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def get_by_stripe_charge(db: Session, stripe_charge_id: str) -> Optional[PaymentModel]:
        dao = (
            db.query(PaymentDAO)
            .where(PaymentDAO.stripe_charge_id == stripe_charge_id)
            .first()
        )
        return PaymentMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def get_by_stripe_intent(db: Session, stripe_payment_intent_id: str) -> Optional[PaymentModel]:
        dao = (
            db.query(PaymentDAO)
            .where(PaymentDAO.stripe_payment_intent_id == stripe_payment_intent_id)
            .first()
        )
        return PaymentMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def list_by_appointment(db: Session, appointment_id: int) -> List[PaymentModel]:
        rows = (
            db.query(PaymentDAO)
            .where(PaymentDAO.appointment_id == appointment_id)
            .order_by(PaymentDAO.id)
            .all()
        )
        return [PaymentMapper.dao_to_model(row) for row in rows]

    @staticmethod
    def get_validated_by_appointment(db: Session, appointment_id: int) -> Optional[PaymentModel]:
        dao = (
            db.query(PaymentDAO)
            .where(PaymentDAO.appointment_id == appointment_id)
            .where(PaymentDAO.status == PaymentStatus.VALIDATED.value)
            .first()
        )
        return PaymentMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def update_status_by_id(db: Session, payment_id: int, status: PaymentStatus) -> Optional[PaymentModel]:
        dao = db.get(PaymentDAO, payment_id)
        if not dao:
            return None
        dao.status = status
        db.flush()
        db.refresh(dao)
        return PaymentMapper.dao_to_model(dao)
