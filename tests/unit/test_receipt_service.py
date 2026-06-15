"""
Tests unitaires — ReceiptService
"""
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from enums.payment_enum import PaymentType
from exceptions.appointment_exceptions import AppointmentNotFound


def _make_receipt(id=1, payment_id=1, appointment_id=10,
                  payment_type=PaymentType.DEPOSIT, amount=Decimal("10.00")):
    r = MagicMock()
    r.id = id
    r.payment_id = payment_id
    r.appointment_id = appointment_id
    r.amount = amount
    r.currency = "eur"
    r.payment_type = payment_type
    r.stripe_receipt_url = "https://pay.stripe.com/receipts/test"
    return r


class TestListByAppointment:
    def test_should_raise_when_appointment_not_found(self):
        # Arrange
        from services.receipt_service import ReceiptService

        with patch("services.receipt_service.AppointmentRepository") as mock_repo:
            mock_repo.get_by_id.return_value = None

            # Act / Assert
            with pytest.raises(AppointmentNotFound):
                ReceiptService.list_by_appointment(appointment_id=99)

    def test_should_return_empty_when_no_receipts(self):
        # Arrange
        from services.receipt_service import ReceiptService

        with patch("services.receipt_service.AppointmentRepository") as mock_appt, \
             patch("services.receipt_service.ReceiptRepository") as mock_receipt:
            mock_appt.get_by_id.return_value = MagicMock()
            mock_receipt.list_by_appointment.return_value = []

            # Act
            result = ReceiptService.list_by_appointment(appointment_id=10)

            # Assert
            assert result == []

    def test_should_return_receipts_list(self):
        # Arrange
        from services.receipt_service import ReceiptService

        deposit_receipt = _make_receipt(id=1, payment_type=PaymentType.DEPOSIT,
                                        amount=Decimal("10.00"))
        balance_receipt = _make_receipt(id=2, payment_type=PaymentType.BALANCE,
                                        amount=Decimal("55.00"))

        with patch("services.receipt_service.AppointmentRepository") as mock_appt, \
             patch("services.receipt_service.ReceiptRepository") as mock_receipt, \
             patch("services.receipt_service.ReceiptMapper") as mock_mapper:
            mock_appt.get_by_id.return_value = MagicMock()
            mock_receipt.list_by_appointment.return_value = [deposit_receipt, balance_receipt]
            mock_mapper.model_to_dto.side_effect = lambda r: MagicMock(
                id=r.id,
                payment_type=r.payment_type,
                amount=r.amount,
            )

            # Act
            result = ReceiptService.list_by_appointment(appointment_id=10)

            # Assert
            assert len(result) == 2
            mock_receipt.list_by_appointment.assert_called_once_with(10)

    def test_should_return_deposit_receipt_with_correct_amount(self):
        # Arrange
        from services.receipt_service import ReceiptService

        receipt = _make_receipt(payment_type=PaymentType.DEPOSIT, amount=Decimal("10.00"))

        with patch("services.receipt_service.AppointmentRepository") as mock_appt, \
             patch("services.receipt_service.ReceiptRepository") as mock_receipt, \
             patch("services.receipt_service.ReceiptMapper") as mock_mapper:
            mock_appt.get_by_id.return_value = MagicMock()
            mock_receipt.list_by_appointment.return_value = [receipt]
            mock_dto = MagicMock()
            mock_dto.amount = Decimal("10.00")
            mock_dto.payment_type = PaymentType.DEPOSIT
            mock_mapper.model_to_dto.return_value = mock_dto

            # Act
            result = ReceiptService.list_by_appointment(appointment_id=10)

            # Assert
            assert result[0].amount == Decimal("10.00")
            assert result[0].payment_type == PaymentType.DEPOSIT
