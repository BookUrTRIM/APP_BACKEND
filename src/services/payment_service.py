import logging
from typing import Any, List, Optional

import stripe
from sqlalchemy.orm import Session

from dtos.payment.payment_create_dto import PaymentCreateDTO
from dtos.payment.payment_intent_response_dto import PaymentIntentResponseDTO
from dtos.payment.payment_response_dto import PaymentResponseDTO
from enums.appointment_enum import AppointmentStatus
from enums.payment_enum import PaymentStatus, PaymentType
from enums.user_enum import UserRole
from exceptions.appointment_exceptions import AppointmentNotFound
from exceptions.payment_exceptions import (
    DepositAlreadyPaid,
    InvalidPaymentAmount,
    NoValidatedPayment,
    PaymentAlreadyProcessed,
    PaymentFailed,
    PaymentNotFound,
)
from mappers.payment_mapper import PaymentMapper
from repositories.appointment_repository import AppointmentRepository
from repositories.availability_repository import AvailabilityRepository
from repositories.client_repository import ClientRepository
from repositories.payment_repository import PaymentRepository
from repositories.provider_repository import ProviderRepository
from repositories.receipt_repository import ReceiptRepository
from repositories.user_account_repository import UserAccountRepository
from services.appointment_service import AppointmentService

logger = logging.getLogger(__name__)


class PaymentService:
    @staticmethod
    def initiate(db: Session, dto: PaymentCreateDTO, user_account_id: int, current_role: UserRole) -> PaymentResponseDTO:
        appointment = AppointmentRepository.get_by_id(db, dto.appointment_id)
        if not appointment:
            raise AppointmentNotFound()

        AppointmentService.assert_access(db, appointment, user_account_id, current_role)

        existing = PaymentRepository.list_by_appointment(db, dto.appointment_id)

        if dto.payment_type == PaymentType.DEPOSIT:
            if any(p.payment_type == PaymentType.DEPOSIT for p in existing):
                raise DepositAlreadyPaid()
            if appointment.deposit_amount is not None:
                if round(float(dto.amount), 2) != round(float(appointment.deposit_amount), 2):
                    raise InvalidPaymentAmount(detail=f"L'acompte attendu est de {appointment.deposit_amount}.")

        if dto.payment_type == PaymentType.BALANCE:
            deposit = next((p for p in existing if p.payment_type == PaymentType.DEPOSIT and p.status.value == 'validated'), None)
            if deposit and appointment.deposit_amount is not None and appointment.service_base_price is not None:
                expected_balance = round(float(appointment.service_base_price) - float(appointment.deposit_amount), 2)
                if round(float(dto.amount), 2) != expected_balance:
                    raise InvalidPaymentAmount(detail=f"Le solde attendu est de {expected_balance}.")

        payment = PaymentRepository.create(db, dto)
        db.commit()
        logger.info("Paiement initié : id=%d appointment_id=%d type=%s", payment.id, payment.appointment_id, payment.payment_type)
        return PaymentMapper.model_to_dto(payment)

    @staticmethod
    def prepare(db: Session, payment_id: int, user_account_id: int, current_role: UserRole) -> PaymentIntentResponseDTO:
        payment = PaymentRepository.get_by_id(db, payment_id)
        if not payment:
            raise PaymentNotFound()

        appointment = AppointmentRepository.get_by_id(db, payment.appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        AppointmentService.assert_access(db, appointment, user_account_id, current_role)

        if payment.stripe_payment_intent_id:
            try:
                intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
            except stripe.StripeError as e:
                logger.error("Échec récupération PaymentIntent Stripe : %s", e)
                raise PaymentFailed()
            return PaymentIntentResponseDTO(payment_id=payment_id, client_secret=intent.client_secret)

        receipt_email = None
        transfer_destination = None
        if appointment:
            client = ClientRepository.get_by_id(db, appointment.client_id)
            if client:
                user = UserAccountRepository.get_by_id(db, client.user_account_id)
                if user:
                    receipt_email = user.email
            provider = ProviderRepository.get_by_id(db, appointment.provider_id)
            if provider and provider.stripe_account_id:
                transfer_destination = provider.stripe_account_id

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),
                currency=payment.currency,
                receipt_email=receipt_email,
                transfer_data={"destination": transfer_destination} if transfer_destination else None,
                metadata={"payment_id": payment.id, "appointment_id": payment.appointment_id},
            )
        except stripe.StripeError as e:
            logger.error("Échec création PaymentIntent Stripe : %s", e)
            raise PaymentFailed()

        PaymentRepository.set_stripe_intent(db, payment_id, intent.id)
        db.commit()
        logger.info("PaymentIntent créé : payment_id=%d pi=%s", payment_id, intent.id)
        return PaymentIntentResponseDTO(payment_id=payment_id, client_secret=intent.client_secret)

    @staticmethod
    def refund_webhook(db: Session, stripe_charge_id: str) -> None:
        payment = PaymentRepository.get_by_stripe_charge(db, stripe_charge_id)
        if not payment:
            raise PaymentNotFound()
        PaymentRepository.refund(db, stripe_charge_id)
        db.commit()
        logger.info("Paiement remboursé : stripe_charge=%s", stripe_charge_id)

    @staticmethod
    def fail_webhook(db: Session, stripe_payment_intent_id: str) -> None:
        payment = PaymentRepository.get_by_stripe_intent(db, stripe_payment_intent_id)
        if not payment:
            raise PaymentNotFound()
        PaymentRepository.fail(db, stripe_payment_intent_id)
        db.commit()
        logger.info("Paiement échoué : stripe_pi=%s", stripe_payment_intent_id)

    @staticmethod
    def confirm_webhook(db: Session, stripe_payment_intent_id: str, stripe_charge_id: str, metadata: Optional[dict[str, Any]] = None) -> PaymentResponseDTO:
        payment = PaymentRepository.get_by_stripe_intent(db, stripe_payment_intent_id)
        if not payment:
            raise PaymentNotFound()
        if payment.paid_at is not None:
            raise PaymentAlreadyProcessed()

        receipt_url = None
        try:
            charge = stripe.Charge.retrieve(stripe_charge_id)
            receipt_url = charge.receipt_url
        except stripe.StripeError as e:
            logger.warning("Impossible de récupérer le receipt_url Stripe : %s", e)

        confirmed = PaymentRepository.confirm(db, stripe_payment_intent_id, stripe_charge_id, metadata, receipt_url)
        if not confirmed:
            raise PaymentFailed()

        ReceiptRepository.create(db, confirmed)
        logger.info("Reçu créé : payment_id=%d type=%s", confirmed.id, confirmed.payment_type)

        if confirmed.payment_type == PaymentType.DEPOSIT:
            appointment = AppointmentRepository.update_status(db, confirmed.appointment_id, AppointmentStatus.CONFIRMED)
            if appointment:
                AvailabilityRepository.create_booked(db, appointment)

        db.commit()
        logger.info("Paiement confirmé : stripe_pi=%s", stripe_payment_intent_id)
        return PaymentMapper.model_to_dto(confirmed)

    @staticmethod
    def refund_by_appointment(db: Session, appointment_id: int, user_account_id: int, current_role: UserRole) -> PaymentResponseDTO:
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        AppointmentService.assert_access(db, appointment, user_account_id, current_role)

        payment = PaymentRepository.get_validated_by_appointment(db, appointment_id)
        if not payment:
            raise NoValidatedPayment()

        try:
            stripe.Refund.create(charge=payment.stripe_charge_id)
        except stripe.StripeError as e:
            logger.error("Échec remboursement Stripe : %s", e)
            raise PaymentFailed()

        refunded = PaymentRepository.update_status_by_id(db, payment.id, PaymentStatus.REFUNDED)
        AppointmentRepository.update_status(db, appointment_id, AppointmentStatus.CANCELLED)
        db.commit()
        logger.info("Remboursement manuel : appointment_id=%d charge=%s", appointment_id, payment.stripe_charge_id)
        return PaymentMapper.model_to_dto(refunded)

    @staticmethod
    def get(db: Session, payment_id: int, user_account_id: int, current_role: UserRole) -> PaymentResponseDTO:
        payment = PaymentRepository.get_by_id(db, payment_id)
        if not payment:
            raise PaymentNotFound()

        appointment = AppointmentRepository.get_by_id(db, payment.appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        AppointmentService.assert_access(db, appointment, user_account_id, current_role)

        return PaymentMapper.model_to_dto(payment)

    @staticmethod
    def list_by_appointment(db: Session, appointment_id: int, user_account_id: int, current_role: UserRole) -> List[PaymentResponseDTO]:
        appointment = AppointmentRepository.get_by_id(db, appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        AppointmentService.assert_access(db, appointment, user_account_id, current_role)

        payments = PaymentRepository.list_by_appointment(db, appointment_id)
        return [PaymentMapper.model_to_dto(p) for p in payments]
