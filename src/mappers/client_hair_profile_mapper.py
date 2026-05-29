from daos.client_hair_profile_dao import ClientHairProfileDAO
from dtos.client.hair_profile_response_dto import HairProfileResponseDTO
from models.client_hair_profile_model import ClientHairProfileModel


class ClientHairProfileMapper:
    @staticmethod
    def dao_to_model(dao: ClientHairProfileDAO) -> ClientHairProfileModel:
        return ClientHairProfileModel(
            id=dao.id,
            client_id=dao.client_id,
            hair_type=dao.hair_type,
            hair_length=dao.hair_length,
        )

    @staticmethod
    def model_to_dto(model: ClientHairProfileModel) -> HairProfileResponseDTO:
        return HairProfileResponseDTO(
            id=model.id,
            client_id=model.client_id,
            hair_type=model.hair_type,
            hair_length=model.hair_length,
        )
