"""
Tests unitaires — PaymentService
"""
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from enums.payment_enum import PaymentStatus, PaymentType
from exceptions.payment_exceptions import (
    DepositAlreadyPaid,
    InvalidPaymentAmount,
    NoValidatedPayment,
    PaymentFailed,
    PaymentNotFound,
)
from exceptions.appointment_exceptions import AppointmentNotFound


def _make_payment(id=1, appointment_id=10, status=PaymentStatus.PENDING,
                  payment_type=PaymentType.DEPOSIT, stripe_pi_id=None, stripe_charge_id=None,
                  paid_at=None):
    p = MagicMock()
    p.id = id
    p.appointment_id = appointment_id
    p.amount = Decimal("20.00")
    p.currency = "eur"
    p.status = status
    p.payment_type = payment_type
    p.stripe_payment_intent_id = stripe_pi_id
    p.stripe_charge_id = stripe_charge_id
    p.paid_at = paid_at
    return p


class TestInitiate:
    def test_should_raise_when_appointment_not_found(self):
        # Arrange
        from services.payment_service import PaymentService
        from dtos.payment.payment_create_dto import PaymentCreateDTO

        dto = PaymentCreateDTO(appointment_id=999, amount=Decimal("20.00"),
                               currency="eur", payment_type=PaymentType.DEPOSIT)
        with patch("services.payment_service.AppointmentRepository") as mock_appt:
            mock_appt.get_by_id.return_value = None

            # Act / Assert
            with pytest.raises(AppointmentNotFound):
                PaymentService.initiate(dto)

    def test_should_raise_when_deposit_already_paid(self):
        # Arrange
        from services.payment_service import PaymentService
        from dtos.payment.payment_create_dto import PaymentCreateDTO

        dto = PaymentCreateDTO(appointment_id=10, amount=Decimal("20.00"),
                               currency="eur", payment_type=PaymentType.DEPOSIT)
        existing = _make_payment(payment_type=PaymentType.DEPOSIT)

        with patch("services.payment_service.AppointmentRepository") as mock_appt, \
             patch("services.payment_service.PaymentRepository") as mock_payment:
            mock_appt.get_by_id.return_value = MagicMock()
            mock_payment.list_by_appointment.return_value = [existing]

            # Act / Assert
            with pytest.raises(DepositAlreadyPaid):
                PaymentService.initiate(dto)

    def test_should_allow_balance_when_deposit_exists(self):
        # Arrange
        from services.payment_service import PaymentService
        from dtos.payment.payment_create_dto import PaymentCreateDTO

        dto = PaymentCreateDTO(appointment_id=10, amount=Decimal("25.00"),
                               currency="eur", payment_type=PaymentType.BALANCE)
        existing_deposit = _make_payment(payment_type=PaymentType.DEPOSIT)
        new_payment = _make_payment(id=2, payment_type=PaymentType.BALANCE)

        with patch("services.payment_service.AppointmentRepository") as mock_appt, \
             patch("services.payment_service.PaymentRepository") as mock_payment, \
             patch("services.payment_service.PaymentMapper") as mock_mapper:
            mock_appt.get_by_id.return_value = MagicMock()
            mock_payment.list_by_appointment.return_value = [existing_deposit]
            mock_payment.create.return_value = new_payment
            mock_mapper.model_to_dto.return_value = MagicMock(payment_type="balance")

            # Act
            result = PaymentService.initiate(dto)

            # Assert
            mock_payment.create.assert_called_once()


class TestPrepare:
    def test_should_raise_when_payment_not_found(self):
        # Arrange
        from services.payment_service import PaymentService

        with patch("services.payment_service.PaymentRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None

            # Act / Assert
            with pytest.raises(PaymentNotFound):
                PaymentService.prepare(payment_id=999)

    def test_should_create_intent_when_no_existing_intent(self):
        # Arrange
        from services.payment_service import PaymentService

        payment = _make_payment(stripe_pi_id=None)
        mock_intent = MagicMock()
        mock_intent.id = "pi_test_123"
        mock_intent.client_secret = "secret_abc"

        with patch("services.payment_service.PaymentRepository") as mock_repo, \
             patch("services.payment_service.AppointmentRepository") as mock_appt, \
             patch("services.payment_service.ClientRepository") as mock_client, \
             patch("services.payment_service.UserAccountRepository") as mock_user, \
             patch("services.payment_service.ProviderRepository") as mock_provider, \
             patch("stripe.PaymentIntent.create", return_value=mock_intent):
            mock_repo.get_by_id.return_value = payment
            mock_appt.get_by_id.return_value = MagicMock(client_id=1, provider_id=2)
            mock_client.get_by_id.return_value = MagicMock(user_account_id=100)
            mock_user.get_by_id.return_value = MagicMock(email="client@test.fr")
            mock_provider.get_by_id.return_value = MagicMock(stripe_account_id=None)

            # Act
            result = PaymentService.prepare(payment_id=1)

            # Assert
            assert result.client_secret == "secret_abc"
            mock_repo.set_stripe_intent.assert_called_once_with(1, "pi_test_123")

    def test_should_retrieve_existing_intent_when_already_prepared(self):
        # Arrange
        from services.payment_service import PaymentService

        payment = _make_payment(stripe_pi_id="pi_existing_456")
        mock_intent = MagicMock()
        mock_intent.client_secret = "existing_secret"

        with patch("services.payment_service.PaymentRepository") as mock_repo, \
             patch("stripe.PaymentIntent.retrieve", return_value=mock_intent):
            mock_repo.get_by_id.return_value = payment

            # Act
            result = PaymentService.prepare(payment_id=1)

            # Assert
            assert result.client_secret == "existing_secret"


class TestRefundByAppointment:
    def test_should_raise_when_no_validated_payment(self):
        # Arrange
        from services.payment_service import PaymentService

        with patch("services.payment_service.PaymentRepository") as mock_repo:
            mock_repo.get_validated_by_appointment.return_value = None

            # Act / Assert
            with pytest.raises(NoValidatedPayment):
                PaymentService.refund_by_appointment(appointment_id=10)

    def test_should_raise_when_stripe_fails(self):
        # Arrange
        from services.payment_service import PaymentService
        import stripe

        payment = _make_payment(status=PaymentStatus.VALIDATED, stripe_charge_id="ch_test")

        with patch("services.payment_service.PaymentRepository") as mock_repo, \
             patch("stripe.Refund.create", side_effect=stripe.StripeError("Stripe error")):
            mock_repo.get_validated_by_appointment.return_value = payment

            # Act / Assert
            with pytest.raises(PaymentFailed):
                PaymentService.refund_by_appointment(appointment_id=10)


class TestConfirmWebhook:
    def test_should_confirm_and_update_appointment_on_deposit(self):
        # Arrange
        from services.payment_service import PaymentService
        from enums.appointment_enum import AppointmentStatus

        confirmed_payment = _make_payment(
            status=PaymentStatus.VALIDATED,
            payment_type=PaymentType.DEPOSIT,
            paid_at=None,
        )
        confirmed_payment.paid_at = None

        with patch("services.payment_service.PaymentRepository") as mock_payment_repo, \
             patch("services.payment_service.AppointmentRepository") as mock_appt_repo, \
             patch("services.payment_service.AvailabilityRepository"), \
             patch("services.payment_service.PaymentMapper") as mock_mapper:
            mock_payment_repo.get_by_stripe_intent.return_value = _make_payment(paid_at=None)
            mock_payment_repo.confirm.return_value = confirmed_payment
            mock_mapper.model_to_dto.return_value = MagicMock()

            # Act
            PaymentService.confirm_webhook("pi_test", "ch_test", {})

            # Assert
            mock_appt_repo.update_status.assert_called_once_with(
                confirmed_payment.appointment_id,
                AppointmentStatus.CONFIRMED
            )


class TestInitiateAmountValidation:
    def _make_appointment(self, deposit_amount=None, service_base_price=None):
        appt = MagicMock()
        appt.id = 10
        appt.deposit_amount = deposit_amount
        appt.service_base_price = service_base_price
        return appt

    def test_should_raise_when_deposit_amount_wrong(self):
        from services.payment_service import PaymentService
        from dtos.payment.payment_create_dto import PaymentCreateDTO

        dto = PaymentCreateDTO(appointment_id=10, amount=Decimal("20.00"),
                               currency="eur", payment_type=PaymentType.DEPOSIT)
        with patch("services.payment_service.AppointmentRepository") as mock_appt, \
             patch("services.payment_service.PaymentRepository") as mock_payment:
            mock_appt.get_by_id.return_value = self._make_appointment(deposit_amount=Decimal("10.00"))
            mock_payment.list_by_appointment.return_value = []

            with pytest.raises(InvalidPaymentAmount):
                PaymentService.initiate(dto)

    def test_should_accept_correct_deposit_amount(self):
        from services.payment_service import PaymentService
        from dtos.payment.payment_create_dto import PaymentCreateDTO

        dto = PaymentCreateDTO(appointment_id=10, amount=Decimal("10.00"),
                               currency="eur", payment_type=PaymentType.DEPOSIT)
        payment = _make_payment()
        with patch("services.payment_service.AppointmentRepository") as mock_appt, \
             patch("services.payment_service.PaymentRepository") as mock_payment, \
             patch("services.payment_service.PaymentMapper") as mock_mapper:
            mock_appt.get_by_id.return_value = self._make_appointment(deposit_amount=Decimal("10.00"))
            mock_payment.list_by_appointment.return_value = []
            mock_payment.create.return_value = payment
            mock_mapper.model_to_dto.return_value = MagicMock()

            PaymentService.initiate(dto)
            mock_payment.create.assert_called_once()

    def test_should_raise_when_balance_amount_wrong(self):
        from services.payment_service import PaymentService
        from dtos.payment.payment_create_dto import PaymentCreateDTO

        dto = PaymentCreateDTO(appointment_id=10, amount=Decimal("30.00"),
                               currency="eur", payment_type=PaymentType.BALANCE)
        validated_deposit = _make_payment(status=PaymentStatus.VALIDATED,
                                          payment_type=PaymentType.DEPOSIT)
        validated_deposit.status = MagicMock()
        validated_deposit.status.value = "validated"

        with patch("services.payment_service.AppointmentRepository") as mock_appt, \
             patch("services.payment_service.PaymentRepository") as mock_payment:
            mock_appt.get_by_id.return_value = self._make_appointment(
                deposit_amount=Decimal("10.00"),
                service_base_price=65.00,
            )
            mock_payment.list_by_appointment.return_value = [validated_deposit]

            with pytest.raises(InvalidPaymentAmount):
                PaymentService.initiate(dto)

    def test_should_accept_correct_balance_amount(self):
        from services.payment_service import PaymentService
        from dtos.payment.payment_create_dto import PaymentCreateDTO

        # balance = 65 - 10 = 55
        dto = PaymentCreateDTO(appointment_id=10, amount=Decimal("55.00"),
                               currency="eur", payment_type=PaymentType.BALANCE)
        validated_deposit = _make_payment(status=PaymentStatus.VALIDATED,
                                          payment_type=PaymentType.DEPOSIT)
        validated_deposit.status = MagicMock()
        validated_deposit.status.value = "validated"
        new_payment = _make_payment(id=2, payment_type=PaymentType.BALANCE)

        with patch("services.payment_service.AppointmentRepository") as mock_appt, \
             patch("services.payment_service.PaymentRepository") as mock_payment, \
             patch("services.payment_service.PaymentMapper") as mock_mapper:
            mock_appt.get_by_id.return_value = self._make_appointment(
                deposit_amount=Decimal("10.00"),
                service_base_price=65.00,
            )
            mock_payment.list_by_appointment.return_value = [validated_deposit]
            mock_payment.create.return_value = new_payment
            mock_mapper.model_to_dto.return_value = MagicMock()

            PaymentService.initiate(dto)
            mock_payment.create.assert_called_once()
