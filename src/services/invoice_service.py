import logging
from decimal import Decimal

from dtos.invoice.invoice_response_dto import InvoiceResponseDTO
from exceptions.appointment_exceptions import AppointmentNotFound, AppointmentNotCompleted
from exceptions.invoice_exceptions import InvoiceAlreadyExists, InvoiceNotFound
from enums.appointment_enum import AppointmentStatus
from mappers.invoice_mapper import InvoiceMapper
from repositories.appointment_repository import AppointmentRepository
from repositories.appointment_service_repository import AppointmentServiceRepository
from repositories.invoice_repository import InvoiceRepository

logger = logging.getLogger(__name__)


class InvoiceService:
    @staticmethod
    def generate(appointment_id: int) -> InvoiceResponseDTO:
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        if appointment.status != AppointmentStatus.COMPLETED:
            raise AppointmentNotCompleted()
        if InvoiceRepository.get_by_appointment(appointment_id):
            raise InvoiceAlreadyExists()

        services = AppointmentServiceRepository.list_by_appointment(appointment_id)
        total_amount = sum(s.billed_price for s in services) or Decimal("0.00")

        invoice = InvoiceRepository.create(appointment_id, total_amount)
        logger.info("Facture générée : id=%d appointment_id=%d total=%s", invoice.id, invoice.appointment_id, total_amount)
        return InvoiceMapper.model_to_dto(invoice)

    @staticmethod
    def get_by_appointment(appointment_id: int) -> InvoiceResponseDTO:
        invoice = InvoiceRepository.get_by_appointment(appointment_id)
        if not invoice:
            raise InvoiceNotFound()
        return InvoiceMapper.model_to_dto(invoice)
