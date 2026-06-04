from typing import List, Optional

from sqlalchemy.orm import Session

from daos.receipt_dao import ReceiptDAO
from mappers.receipt_mapper import ReceiptMapper
from models.payment_model import PaymentModel
from models.receipt_model import ReceiptModel


class ReceiptRepository:
    @staticmethod
    def create(db: Session, payment: PaymentModel) -> ReceiptModel:
        dao = ReceiptDAO(
            payment_id=payment.id,
            appointment_id=payment.appointment_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_type=payment.payment_type.value if hasattr(payment.payment_type, 'value') else payment.payment_type,
            stripe_receipt_url=payment.stripe_receipt_url,
        )
        db.add(dao)
        db.flush()
        db.refresh(dao)
        return ReceiptMapper.dao_to_model(dao)

    @staticmethod
    def get_by_payment(db: Session, payment_id: int) -> Optional[ReceiptModel]:
        dao = (
            db.query(ReceiptDAO)
            .where(ReceiptDAO.payment_id == payment_id)
            .first()
        )
        return ReceiptMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def list_by_appointment(db: Session, appointment_id: int) -> List[ReceiptModel]:
        rows = (
            db.query(ReceiptDAO)
            .where(ReceiptDAO.appointment_id == appointment_id)
            .order_by(ReceiptDAO.issued_at)
            .all()
        )
        return [ReceiptMapper.dao_to_model(row) for row in rows]
