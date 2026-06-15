"""
Tests unitaires — InvoiceService
"""
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from enums.appointment_enum import AppointmentStatus
from exceptions.appointment_exceptions import AppointmentNotCompleted, AppointmentNotFound
from exceptions.invoice_exceptions import InvoiceAlreadyExists, InvoiceNotFound


def _make_appointment(id=10, status=AppointmentStatus.COMPLETED):
    a = MagicMock()
    a.id = id
    a.status = status
    return a


class TestGenerate:
    def test_should_raise_when_appointment_not_found(self):
        from services.invoice_service import InvoiceService

        with patch("services.invoice_service.AppointmentRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None

            with pytest.raises(AppointmentNotFound):
                InvoiceService.generate(appointment_id=99)

    def test_should_raise_when_appointment_not_completed(self):
        from services.invoice_service import InvoiceService

        with patch("services.invoice_service.AppointmentRepository") as mock_repo:
            mock_repo.get_by_id.return_value = _make_appointment(
                status=AppointmentStatus.CONFIRMED
            )

            with pytest.raises(AppointmentNotCompleted):
                InvoiceService.generate(appointment_id=10)

    def test_should_raise_when_invoice_already_exists(self):
        from services.invoice_service import InvoiceService

        with patch("services.invoice_service.AppointmentRepository") as mock_appt, \
             patch("services.invoice_service.InvoiceRepository") as mock_invoice:
            mock_appt.get_by_id.return_value = _make_appointment()
            mock_invoice.get_by_appointment.return_value = MagicMock()

            with pytest.raises(InvoiceAlreadyExists):
                InvoiceService.generate(appointment_id=10)

    def test_should_generate_invoice_with_zero_when_no_services(self):
        from services.invoice_service import InvoiceService

        new_invoice = MagicMock()
        new_invoice.id = 1
        new_invoice.total_amount = Decimal("0.00")

        with patch("services.invoice_service.AppointmentRepository") as mock_appt, \
             patch("services.invoice_service.InvoiceRepository") as mock_invoice, \
             patch("services.invoice_service.AppointmentServiceRepository") as mock_appt_svc, \
             patch("services.invoice_service.InvoiceMapper") as mock_mapper:
            mock_appt.get_by_id.return_value = _make_appointment()
            mock_invoice.get_by_appointment.return_value = None
            mock_appt_svc.list_by_appointment.return_value = []
            mock_invoice.create.return_value = new_invoice
            mock_mapper.model_to_dto.return_value = MagicMock(total_amount=Decimal("0.00"))

            result = InvoiceService.generate(appointment_id=10)

            mock_invoice.create.assert_called_once_with(10, Decimal("0.00"), None)

    def test_should_sum_billed_prices_when_services_exist(self):
        from services.invoice_service import InvoiceService

        svc1 = MagicMock()
        svc1.billed_price = Decimal("45.00")
        svc2 = MagicMock()
        svc2.billed_price = Decimal("15.00")

        with patch("services.invoice_service.AppointmentRepository") as mock_appt, \
             patch("services.invoice_service.InvoiceRepository") as mock_invoice, \
             patch("services.invoice_service.AppointmentServiceRepository") as mock_appt_svc, \
             patch("services.invoice_service.InvoiceMapper") as mock_mapper:
            mock_appt.get_by_id.return_value = _make_appointment()
            mock_invoice.get_by_appointment.return_value = None
            mock_appt_svc.list_by_appointment.return_value = [svc1, svc2]
            mock_invoice.create.return_value = MagicMock()
            mock_mapper.model_to_dto.return_value = MagicMock(total_amount=Decimal("60.00"))

            InvoiceService.generate(appointment_id=10)

            mock_invoice.create.assert_called_once_with(10, Decimal("60.00"), None)

    def test_should_populate_pdf_url_from_stripe_receipt(self):
        # Arrange
        from services.invoice_service import InvoiceService

        validated_payment = MagicMock()
        validated_payment.stripe_receipt_url = "https://pay.stripe.com/receipts/test"

        with patch("services.invoice_service.AppointmentRepository") as mock_appt, \
             patch("services.invoice_service.InvoiceRepository") as mock_invoice, \
             patch("services.invoice_service.AppointmentServiceRepository") as mock_appt_svc, \
             patch("services.invoice_service.PaymentRepository") as mock_payment, \
             patch("services.invoice_service.InvoiceMapper") as mock_mapper:
            mock_appt.get_by_id.return_value = _make_appointment()
            mock_invoice.get_by_appointment.return_value = None
            mock_appt_svc.list_by_appointment.return_value = []
            mock_payment.get_validated_by_appointment.return_value = validated_payment
            mock_invoice.create.return_value = MagicMock()
            mock_mapper.model_to_dto.return_value = MagicMock()

            # Act
            InvoiceService.generate(appointment_id=10)

            # Assert — pdf_url = receipt_url du paiement validé
            mock_invoice.create.assert_called_once_with(
                10, Decimal("0.00"), "https://pay.stripe.com/receipts/test"
            )

    def test_should_generate_with_null_pdf_url_when_no_payment(self):
        # Arrange
        from services.invoice_service import InvoiceService

        with patch("services.invoice_service.AppointmentRepository") as mock_appt, \
             patch("services.invoice_service.InvoiceRepository") as mock_invoice, \
             patch("services.invoice_service.AppointmentServiceRepository") as mock_appt_svc, \
             patch("services.invoice_service.PaymentRepository") as mock_payment, \
             patch("services.invoice_service.InvoiceMapper") as mock_mapper:
            mock_appt.get_by_id.return_value = _make_appointment()
            mock_invoice.get_by_appointment.return_value = None
            mock_appt_svc.list_by_appointment.return_value = []
            mock_payment.get_validated_by_appointment.return_value = None
            mock_invoice.create.return_value = MagicMock()
            mock_mapper.model_to_dto.return_value = MagicMock()

            # Act
            InvoiceService.generate(appointment_id=10)

            # Assert — pdf_url = None si pas de paiement
            mock_invoice.create.assert_called_once_with(10, Decimal("0.00"), None)


class TestGetByAppointment:
    def test_should_raise_when_not_found(self):
        from services.invoice_service import InvoiceService

        with patch("services.invoice_service.InvoiceRepository") as mock_repo:
            mock_repo.get_by_appointment.return_value = None

            with pytest.raises(InvoiceNotFound):
                InvoiceService.get_by_appointment(appointment_id=99)

    def test_should_return_invoice_when_found(self):
        from services.invoice_service import InvoiceService

        invoice = MagicMock()
        with patch("services.invoice_service.InvoiceRepository") as mock_repo, \
             patch("services.invoice_service.InvoiceMapper") as mock_mapper:
            mock_repo.get_by_appointment.return_value = invoice
            mock_mapper.model_to_dto.return_value = MagicMock(id=1)

            result = InvoiceService.get_by_appointment(appointment_id=10)

            assert result.id == 1
