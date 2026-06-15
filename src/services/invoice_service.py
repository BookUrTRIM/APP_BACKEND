import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from dtos.invoice.invoice_response_dto import InvoiceResponseDTO
from enums.appointment_enum import AppointmentStatus
from enums.user_enum import UserRole
from exceptions.appointment_exceptions import AppointmentNotCompleted, AppointmentNotFound
from exceptions.invoice_exceptions import InvoiceAlreadyExists, InvoiceNotFound
from mappers.invoice_mapper import InvoiceMapper
from repositories.appointment_repository import AppointmentRepository
from repositories.appointment_service_repository import AppointmentServiceRepository
from repositories.invoice_repository import InvoiceRepository
from repositories.payment_repository import PaymentRepository
from services.appointment_service import AppointmentService

logger = logging.getLogger(__name__)


class InvoiceService:
    @staticmethod
    def generate(db: Session, appointment_id: int, user_account_id: int, current_role: UserRole) -> InvoiceResponseDTO:
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        AppointmentService.assert_access(db, appointment, user_account_id, current_role)
        if appointment.status != AppointmentStatus.COMPLETED:
            raise AppointmentNotCompleted()
        if InvoiceRepository.get_by_appointment(db, appointment_id):
            raise InvoiceAlreadyExists()

        services = AppointmentServiceRepository.list_by_appointment(db, appointment_id)
        total_amount = sum(s.billed_price for s in services) or Decimal("0.00")

        receipt_url = None
        validated_payment = PaymentRepository.get_validated_by_appointment(db, appointment_id)
        if validated_payment:
            receipt_url = validated_payment.stripe_receipt_url

        invoice = InvoiceRepository.create(db, appointment_id, total_amount, receipt_url)
        db.commit()
        logger.info("Facture générée : id=%d appointment_id=%d total=%s", invoice.id, invoice.appointment_id, total_amount)
        return InvoiceMapper.model_to_dto(invoice)

    @staticmethod
    def get_by_appointment(db: Session, appointment_id: int, user_account_id: int, current_role: UserRole) -> InvoiceResponseDTO:
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        AppointmentService.assert_access(db, appointment, user_account_id, current_role)

        invoice = InvoiceRepository.get_by_appointment(db, appointment_id)
        if not invoice:
            raise InvoiceNotFound()
        return InvoiceMapper.model_to_dto(invoice)
