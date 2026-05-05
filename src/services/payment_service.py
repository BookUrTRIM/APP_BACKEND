import logging
from typing import Any, List, Optional

from dtos.payment.payment_create_dto import PaymentCreateDTO
from dtos.payment.payment_response_dto import PaymentResponseDTO
from enums.payment_enum import PaymentType
from exceptions.appointment_exceptions import AppointmentNotFound
from exceptions.payment_exceptions import (
    DepositAlreadyPaid,
    PaymentAlreadyProcessed,
    PaymentFailed,
    PaymentNotFound,
)
from mappers.payment_mapper import PaymentMapper
from repositories.appointment_repository import AppointmentRepository
from repositories.payment_repository import PaymentRepository

logger = logging.getLogger(__name__)


class PaymentService:
    @staticmethod
    def initiate(dto: PaymentCreateDTO) -> PaymentResponseDTO:
        if not AppointmentRepository.get_by_id(dto.appointment_id):
            raise AppointmentNotFound()

        if dto.payment_type == PaymentType.DEPOSIT:
            existing = PaymentRepository.list_by_appointment(dto.appointment_id)
            if any(p.payment_type == PaymentType.DEPOSIT for p in existing):
                raise DepositAlreadyPaid()

        payment = PaymentRepository.create(dto)
        logger.info("Paiement initié : id=%d appointment_id=%d type=%s", payment.id, payment.appointment_id, payment.payment_type)
        return PaymentMapper.model_to_dto(payment)

    @staticmethod
    def confirm_webhook(
        stripe_payment_intent_id: str,
        stripe_charge_id: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> PaymentResponseDTO:
        payment = PaymentRepository.get_by_stripe_intent(stripe_payment_intent_id)
        if not payment:
            raise PaymentNotFound()
        if payment.paid_at is not None:
            raise PaymentAlreadyProcessed()

        confirmed = PaymentRepository.confirm(stripe_payment_intent_id, stripe_charge_id, metadata)
        if not confirmed:
            raise PaymentFailed()

        logger.info("Paiement confirmé : stripe_pi=%s", stripe_payment_intent_id)
        return PaymentMapper.model_to_dto(confirmed)

    @staticmethod
    def get(payment_id: int) -> PaymentResponseDTO:
        payment = PaymentRepository.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFound()
        return PaymentMapper.model_to_dto(payment)

    @staticmethod
    def list_by_appointment(appointment_id: int) -> List[PaymentResponseDTO]:
        payments = PaymentRepository.list_by_appointment(appointment_id)
        return [PaymentMapper.model_to_dto(p) for p in payments]
