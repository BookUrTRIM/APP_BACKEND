from daos.receipt_dao import ReceiptDAO
from dtos.receipt.receipt_response_dto import ReceiptResponseDTO
from models.receipt_model import ReceiptModel


class ReceiptMapper:
    @staticmethod
    def dao_to_model(dao: ReceiptDAO) -> ReceiptModel:
        return ReceiptModel(
            id=dao.id,
            payment_id=dao.payment_id,
            appointment_id=dao.appointment_id,
            amount=dao.amount,
            currency=dao.currency,
            payment_type=dao.payment_type,
            issued_at=dao.issued_at,
            stripe_receipt_url=dao.stripe_receipt_url,
        )

    @staticmethod
    def model_to_dto(model: ReceiptModel) -> ReceiptResponseDTO:
        return ReceiptResponseDTO(
            id=model.id,
            payment_id=model.payment_id,
            appointment_id=model.appointment_id,
            amount=model.amount,
            currency=model.currency,
            payment_type=model.payment_type,
            issued_at=model.issued_at,
            stripe_receipt_url=model.stripe_receipt_url,
        )
