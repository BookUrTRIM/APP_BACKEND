import logging
from typing import Any, List, Optional

import stripe

from dtos.payment.payment_create_dto import PaymentCreateDTO
from dtos.payment.payment_intent_response_dto import PaymentIntentResponseDTO
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
    def prepare(payment_id: int) -> PaymentIntentResponseDTO:
        payment = PaymentRepository.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFound()

        if payment.stripe_payment_intent_id:
            try:
                intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
            except stripe.StripeError as e:
                logger.error("Échec récupération PaymentIntent Stripe : %s", e)
                raise PaymentFailed()
            return PaymentIntentResponseDTO(payment_id=payment_id, client_secret=intent.client_secret)

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),
                currency=payment.currency,
                metadata={"payment_id": payment.id, "appointment_id": payment.appointment_id},
            )
        except stripe.StripeError as e:
            logger.error("Échec création PaymentIntent Stripe : %s", e)
            raise PaymentFailed()

        PaymentRepository.set_stripe_intent(payment_id, intent.id)
        logger.info("PaymentIntent créé : payment_id=%d pi=%s", payment_id, intent.id)
        return PaymentIntentResponseDTO(payment_id=payment_id, client_secret=intent.client_secret)

    @staticmethod
    def refund_webhook(stripe_charge_id: str) -> None:
        payment = PaymentRepository.get_by_stripe_charge(stripe_charge_id)
        if not payment:
            raise PaymentNotFound()
        PaymentRepository.refund(stripe_charge_id)
        logger.info("Paiement remboursé : stripe_charge=%s", stripe_charge_id)

    @staticmethod
    def fail_webhook(stripe_payment_intent_id: str) -> None:
        payment = PaymentRepository.get_by_stripe_intent(stripe_payment_intent_id)
        if not payment:
            raise PaymentNotFound()
        PaymentRepository.fail(stripe_payment_intent_id)
        logger.info("Paiement échoué : stripe_pi=%s", stripe_payment_intent_id)

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
