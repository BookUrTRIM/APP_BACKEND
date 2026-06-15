from daos.availability_dao import AvailabilityDAO
from models.availability_model import AvailabilityModel
from dtos.availability.availability_response_dto import AvailabilityResponseDTO


class AvailabilityMapper:
    @staticmethod
    def dao_to_model(dao: AvailabilityDAO) -> AvailabilityModel:
        return AvailabilityModel(
            id=dao.id,
            provider_id=dao.provider_id,
            day_date=dao.day_date,
            start_time=dao.start_time,
            end_time=dao.end_time,
            slot_type=dao.slot_type,
            created_at=dao.created_at,
            updated_at=dao.updated_at,
        )

    @staticmethod
    def model_to_dto(model: AvailabilityModel) -> AvailabilityResponseDTO:
        return AvailabilityResponseDTO(
            id=model.id,
            provider_id=model.provider_id,
            day_date=model.day_date,
            start_time=model.start_time,
            end_time=model.end_time,
            slot_type=model.slot_type,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
