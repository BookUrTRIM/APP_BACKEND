from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from daos.invoice_dao import InvoiceDAO
from mappers.invoice_mapper import InvoiceMapper
from models.invoice_model import InvoiceModel


class InvoiceRepository:
    @staticmethod
    def create(db: Session, appointment_id: int, total_amount: Decimal, pdf_url: Optional[str] = None) -> InvoiceModel:
        dao = InvoiceDAO(
            appointment_id=appointment_id,
            total_amount=total_amount,
            pdf_url=pdf_url,
        )
        db.add(dao)
        db.flush()
        db.refresh(dao)
        return InvoiceMapper.dao_to_model(dao)

    @staticmethod
    def get_by_appointment(db: Session, appointment_id: int) -> Optional[InvoiceModel]:
        dao = db.query(InvoiceDAO).where(InvoiceDAO.appointment_id == appointment_id).first()
        return InvoiceMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def set_pdf_url(db: Session, appointment_id: int, pdf_url: str) -> Optional[InvoiceModel]:
        dao = db.query(InvoiceDAO).where(InvoiceDAO.appointment_id == appointment_id).first()
        if not dao:
            return None
        dao.pdf_url = pdf_url
        db.flush()
        db.refresh(dao)
        return InvoiceMapper.dao_to_model(dao)
