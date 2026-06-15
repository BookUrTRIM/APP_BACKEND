from daos.appointment_service_dao import AppointmentServiceDAO
from models.appointment_service_model import AppointmentServiceModel
from dtos.appointment.appointment_service_response_dto import AppointmentServiceResponseDTO


class AppointmentServiceMapper:
    @staticmethod
    def dao_to_model(dao: AppointmentServiceDAO) -> AppointmentServiceModel:
        return AppointmentServiceModel(
            appointment_id=dao.appointment_id,
            service_id=dao.service_id,
            adjusted_duration=dao.adjusted_duration,
            billed_price=dao.billed_price,
        )

    @staticmethod
    def model_to_dto(model: AppointmentServiceModel) -> AppointmentServiceResponseDTO:
        return AppointmentServiceResponseDTO(
            appointment_id=model.appointment_id,
            service_id=model.service_id,
            adjusted_duration=model.adjusted_duration,
            billed_price=model.billed_price,
        )
