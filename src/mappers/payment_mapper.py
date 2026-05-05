from daos.payment_dao import PaymentDAO
from models.payment_model import PaymentModel
from dtos.payment.payment_response_dto import PaymentResponseDTO


class PaymentMapper:
    @staticmethod
    def dao_to_model(dao: PaymentDAO) -> PaymentModel:
        return PaymentModel(
            id=dao.id,
            appointment_id=dao.appointment_id,
            amount=dao.amount,
            currency=dao.currency,
            payment_type=dao.payment_type,
            status=dao.status,
            paid_at=dao.paid_at,
            stripe_payment_intent_id=dao.stripe_payment_intent_id,
            stripe_charge_id=dao.stripe_charge_id,
            stripe_metadata=dao.stripe_metadata,
        )

    @staticmethod
    def model_to_dto(model: PaymentModel) -> PaymentResponseDTO:
        return PaymentResponseDTO(
            id=model.id,
            appointment_id=model.appointment_id,
            amount=model.amount,
            currency=model.currency,
            payment_type=model.payment_type,
            status=model.status,
            paid_at=model.paid_at,
            stripe_payment_intent_id=model.stripe_payment_intent_id,
            stripe_charge_id=model.stripe_charge_id,
            stripe_metadata=model.stripe_metadata,
        )
