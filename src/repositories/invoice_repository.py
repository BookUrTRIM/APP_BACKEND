from decimal import Decimal
from typing import Optional

from daos.invoice_dao import InvoiceDAO
from mappers.invoice_mapper import InvoiceMapper
from models.invoice_model import InvoiceModel
from shared.db import get_db_session


class InvoiceRepository:
    @staticmethod
    def create(appointment_id: int, total_amount: Decimal, pdf_url: Optional[str] = None) -> InvoiceModel:
        session = get_db_session()

        dao = InvoiceDAO(
            appointment_id=appointment_id,
            total_amount=total_amount,
            pdf_url=pdf_url,
        )
        session.add(dao)
        session.commit()
        session.refresh(dao)
        return InvoiceMapper.dao_to_model(dao)

    @staticmethod
    def get_by_appointment(appointment_id: int) -> Optional[InvoiceModel]:
        session = get_db_session()
        dao = session.query(InvoiceDAO).where(InvoiceDAO.appointment_id == appointment_id).first()
        return InvoiceMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def set_pdf_url(appointment_id: int, pdf_url: str) -> Optional[InvoiceModel]:
        session = get_db_session()
        dao = session.query(InvoiceDAO).where(InvoiceDAO.appointment_id == appointment_id).first()
        if not dao:
            return None

        dao.pdf_url = pdf_url
        session.commit()
        session.refresh(dao)
        return InvoiceMapper.dao_to_model(dao)
