from typing import List, Optional

from daos.receipt_dao import ReceiptDAO
from mappers.receipt_mapper import ReceiptMapper
from models.payment_model import PaymentModel
from models.receipt_model import ReceiptModel
from shared.db import get_db_session


class ReceiptRepository:
    @staticmethod
    def create(payment: PaymentModel) -> ReceiptModel:
        session = get_db_session()
        dao = ReceiptDAO(
            payment_id=payment.id,
            appointment_id=payment.appointment_id,
            amount=payment.amount,
            currency=payment.currency,
            payment_type=payment.payment_type.value if hasattr(payment.payment_type, 'value') else payment.payment_type,
            stripe_receipt_url=payment.stripe_receipt_url,
        )
        session.add(dao)
        session.commit()
        session.refresh(dao)
        return ReceiptMapper.dao_to_model(dao)

    @staticmethod
    def get_by_payment(payment_id: int) -> Optional[ReceiptModel]:
        session = get_db_session()
        dao = (
            session.query(ReceiptDAO)
            .where(ReceiptDAO.payment_id == payment_id)
            .first()
        )
        return ReceiptMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def list_by_appointment(appointment_id: int) -> List[ReceiptModel]:
        session = get_db_session()
        rows = (
            session.query(ReceiptDAO)
            .where(ReceiptDAO.appointment_id == appointment_id)
            .order_by(ReceiptDAO.issued_at)
            .all()
        )
        return [ReceiptMapper.dao_to_model(row) for row in rows]
