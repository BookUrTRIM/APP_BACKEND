import logging
from typing import List, Optional, Tuple

import stripe

from dtos.appointment.appointment_create_dto import AppointmentCreateDTO
from dtos.appointment.appointment_response_dto import AppointmentResponseDTO
from dtos.appointment.appointment_update_dto import AppointmentUpdateDTO
from enums.appointment_enum import AppointmentStatus
from enums.payment_enum import PaymentStatus
from enums.user_enum import UserRole
from exceptions.appointment_exceptions import (
    AppointmentAccessDenied,
    AppointmentAlreadyCancelled,
    AppointmentNotFound,
    InvalidStatusTransition,
    TooManyPendingAppointments,
)
from exceptions.client_exceptions import ClientNotFound
from exceptions.payment_exceptions import PaymentFailed
from exceptions.provider_exceptions import ProviderNotFound
from mappers.appointment_mapper import AppointmentMapper
from repositories.appointment_repository import AppointmentRepository
from repositories.availability_repository import AvailabilityRepository
from repositories.client_repository import ClientRepository
from repositories.payment_repository import PaymentRepository
from repositories.provider_repository import ProviderRepository

logger = logging.getLogger(__name__)

_VALID_TRANSITIONS: dict[AppointmentStatus, set[AppointmentStatus]] = {
    AppointmentStatus.PENDING: {AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED},
    AppointmentStatus.CONFIRMED: {AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED},
    AppointmentStatus.COMPLETED: set(),
    AppointmentStatus.CANCELLED: set(),
    AppointmentStatus.EXPIRED: set(),
}


class AppointmentService:
    @staticmethod
    def book(user_account_id: int, dto: AppointmentCreateDTO) -> AppointmentResponseDTO:
        client = ClientRepository.get_by_user_account_id(user_account_id)
        if not client:
            raise ClientNotFound()

        if not ProviderRepository.get_by_id(dto.provider_id):
            raise ProviderNotFound()

        if AppointmentRepository.count_pending_by_client(client.id) >= 2:
            raise TooManyPendingAppointments()

        appointment = AppointmentRepository.create(dto, client.id)
        logger.info("RDV créé : id=%d client_id=%d provider_id=%d", appointment.id, appointment.client_id, appointment.provider_id)
        return AppointmentMapper.model_to_dto(appointment)

    @staticmethod
    def update(
        appointment_id: int,
        user_account_id: int,
        current_role: UserRole,
        dto: AppointmentUpdateDTO,
    ) -> AppointmentResponseDTO:
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFound()

        AppointmentService._assert_access(appointment, user_account_id, current_role)

        if dto.status is not None:
            AppointmentService._assert_valid_transition(appointment.status, dto.status)

        updated = AppointmentRepository.update(appointment_id, dto)
        return AppointmentMapper.model_to_dto(updated)

    @staticmethod
    def cancel_by_client(appointment_id: int, user_account_id: int) -> AppointmentResponseDTO:
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        if appointment.status == AppointmentStatus.CANCELLED:
            raise AppointmentAlreadyCancelled()

        client = ClientRepository.get_by_user_account_id(user_account_id)
        if not client or appointment.client_id != client.id:
            raise AppointmentAccessDenied()

        AppointmentService._assert_valid_transition(appointment.status, AppointmentStatus.CANCELLED)
        updated = AppointmentRepository.update(appointment_id, AppointmentUpdateDTO(status=AppointmentStatus.CANCELLED))
        if appointment.status == AppointmentStatus.CONFIRMED:
            AvailabilityRepository.delete_booked(appointment.provider_id, appointment.start_at)
        logger.info("RDV annulé par client : id=%d", appointment_id)
        return AppointmentMapper.model_to_dto(updated)

    @staticmethod
    def cancel_by_provider(appointment_id: int, user_account_id: int) -> AppointmentResponseDTO:
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        if appointment.status == AppointmentStatus.CANCELLED:
            raise AppointmentAlreadyCancelled()

        provider = ProviderRepository.get_by_user_account_id(user_account_id)
        if not provider or appointment.provider_id != provider.id:
            raise AppointmentAccessDenied()

        AppointmentService._assert_valid_transition(appointment.status, AppointmentStatus.CANCELLED)
        updated = AppointmentRepository.update(appointment_id, AppointmentUpdateDTO(status=AppointmentStatus.CANCELLED))
        if appointment.status == AppointmentStatus.CONFIRMED:
            AvailabilityRepository.delete_booked(appointment.provider_id, appointment.start_at)

        payment = PaymentRepository.get_validated_by_appointment(appointment_id)
        if payment and payment.stripe_charge_id:
            try:
                stripe.Refund.create(charge=payment.stripe_charge_id)
                PaymentRepository.update_status_by_id(payment.id, PaymentStatus.REFUNDED)
                logger.info("Remboursement Stripe suite à annulation provider : charge=%s", payment.stripe_charge_id)
            except stripe.StripeError as e:
                logger.error("Échec remboursement Stripe lors annulation provider : %s", e)
                AppointmentRepository.update_status(appointment_id, appointment.status)
                raise PaymentFailed()

        logger.info("RDV annulé par provider : id=%d", appointment_id)
        return AppointmentMapper.model_to_dto(updated)

    @staticmethod
    def complete(appointment_id: int, user_account_id: int) -> AppointmentResponseDTO:
        from services.invoice_service import InvoiceService
        from exceptions.invoice_exceptions import InvoiceAlreadyExists

        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFound()

        provider = ProviderRepository.get_by_user_account_id(user_account_id)
        if not provider or appointment.provider_id != provider.id:
            raise AppointmentAccessDenied()

        AppointmentService._assert_valid_transition(appointment.status, AppointmentStatus.COMPLETED)
        updated = AppointmentRepository.update_status(appointment_id, AppointmentStatus.COMPLETED)

        try:
            InvoiceService.generate(appointment_id)
        except InvoiceAlreadyExists:
            pass

        logger.info("RDV complété : id=%d", appointment_id)
        return AppointmentMapper.model_to_dto(updated)

    @staticmethod
    def cancel(appointment_id: int, user_account_id: int, current_role: UserRole) -> AppointmentResponseDTO:
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        if appointment.status == AppointmentStatus.CANCELLED:
            raise AppointmentAlreadyCancelled()

        AppointmentService._assert_access(appointment, user_account_id, current_role)
        AppointmentService._assert_valid_transition(appointment.status, AppointmentStatus.CANCELLED)

        updated = AppointmentRepository.update(appointment_id, AppointmentUpdateDTO(status=AppointmentStatus.CANCELLED))
        logger.info("RDV annulé : id=%d", appointment_id)
        return AppointmentMapper.model_to_dto(updated)

    @staticmethod
    def get(appointment_id: int, user_account_id: int, current_role: UserRole) -> AppointmentResponseDTO:
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise AppointmentNotFound()
        AppointmentService._assert_access(appointment, user_account_id, current_role)
        return AppointmentMapper.model_to_dto(appointment)

    @staticmethod
    def list_by_client(
        user_account_id: int,
        status: Optional[AppointmentStatus] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[AppointmentResponseDTO], int]:
        client = ClientRepository.get_by_user_account_id(user_account_id)
        if not client:
            raise ClientNotFound()

        appointments, total = AppointmentRepository.list_by_client(client.id, status=status, page=page, limit=limit)
        return [AppointmentMapper.model_to_dto(a) for a in appointments], total

    @staticmethod
    def list_by_provider(
        user_account_id: int,
        status: Optional[AppointmentStatus] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[AppointmentResponseDTO], int]:
        provider = ProviderRepository.get_by_user_account_id(user_account_id)
        if not provider:
            raise ProviderNotFound()

        appointments, total = AppointmentRepository.list_by_provider(provider.id, status=status, page=page, limit=limit)
        return [AppointmentMapper.model_to_dto(a) for a in appointments], total

    # ── helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _assert_access(appointment, user_account_id: int, current_role: UserRole) -> None:
        client = ClientRepository.get_by_id(appointment.client_id)
        provider = ProviderRepository.get_by_id(appointment.provider_id)

        is_owner = (client and client.user_account_id == user_account_id) or \
                   (provider and provider.user_account_id == user_account_id)

        if not is_owner:
            raise AppointmentAccessDenied()

    @staticmethod
    def _assert_valid_transition(current: AppointmentStatus, target: AppointmentStatus) -> None:
        if target not in _VALID_TRANSITIONS.get(current, set()):
            raise InvalidStatusTransition(
                detail=f"Transition '{current.value}' → '{target.value}' non autorisée."
            )
