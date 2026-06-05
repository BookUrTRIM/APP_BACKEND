import logging
from typing import List

from sqlalchemy.orm import Session

from dtos.receipt.receipt_response_dto import ReceiptResponseDTO
from exceptions.appointment_exceptions import AppointmentNotFound
from mappers.receipt_mapper import ReceiptMapper
from repositories.appointment_repository import AppointmentRepository
from repositories.receipt_repository import ReceiptRepository

logger = logging.getLogger(__name__)


class ReceiptService:
    @staticmethod
    def list_by_appointment(db: Session, appointment_id: int) -> List[ReceiptResponseDTO]:
        if not AppointmentRepository.get_by_id(db, appointment_id):
            raise AppointmentNotFound()
        receipts = ReceiptRepository.list_by_appointment(db, appointment_id)
        return [ReceiptMapper.model_to_dto(r) for r in receipts]
