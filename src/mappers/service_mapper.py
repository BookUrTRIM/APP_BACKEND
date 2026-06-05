from daos.service_dao import ServiceDAO
from models.service_model import ServiceModel
from dtos.service.service_response_dto import ServiceResponseDTO


class ServiceMapper:
    @staticmethod
    def dao_to_model(dao: ServiceDAO) -> ServiceModel:
        return ServiceModel(
            id=dao.id,
            provider_id=dao.provider_id,
            name=dao.name,
            description=dao.description,
            default_duration=dao.default_duration,
            base_price=dao.base_price,
            deposit_amount=dao.deposit_amount,
            created_at=dao.created_at,
            updated_at=dao.updated_at,
        )

    @staticmethod
    def model_to_dto(model: ServiceModel) -> ServiceResponseDTO:
        return ServiceResponseDTO(
            id=model.id,
            provider_id=model.provider_id,
            name=model.name,
            description=model.description,
            default_duration=model.default_duration,
            base_price=model.base_price,
            deposit_amount=model.deposit_amount,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
