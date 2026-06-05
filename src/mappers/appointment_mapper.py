from daos.appointment_dao import AppointmentDAO
from models.appointment_model import AppointmentModel
from dtos.appointment.appointment_response_dto import AppointmentResponseDTO


class AppointmentMapper:
    @staticmethod
    def dao_to_model(dao: AppointmentDAO) -> AppointmentModel:
        return AppointmentModel(
            id=dao.id,
            client_id=dao.client_id,
            provider_id=dao.provider_id,
            start_at=dao.start_at,
            end_at=dao.end_at,
            status=dao.status,
            products_used=dao.products_used,
            specific_request=dao.specific_request,
            answers=dao.answers,
            deposit_amount=float(dao.deposit_amount) if dao.deposit_amount is not None else None,
            service_name=None,
            service_base_price=None,
            created_at=dao.created_at,
            updated_at=dao.updated_at,
        )

    @staticmethod
    def model_to_dto(model: AppointmentModel) -> AppointmentResponseDTO:
        return AppointmentResponseDTO(
            id=model.id,
            client_id=model.client_id,
            provider_id=model.provider_id,
            start_at=model.start_at,
            end_at=model.end_at,
            status=model.status,
            products_used=model.products_used,
            specific_request=model.specific_request,
            answers=model.answers,
            deposit_amount=model.deposit_amount,
            service_name=model.service_name,
            service_base_price=model.service_base_price,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
