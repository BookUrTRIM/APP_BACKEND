from daos.client_dao import ClientDAO
from models.client_model import ClientModel
from dtos.client.client_response_dto import ClientResponseDTO


class ClientMapper:
    @staticmethod
    def dao_to_model(dao: ClientDAO) -> ClientModel:
        return ClientModel(
            id=dao.id,
            user_account_id=dao.user_account_id,
            last_name=dao.last_name,
            first_name=dao.first_name,
            phone=dao.phone,
            gender=dao.gender,
            hair_length=dao.hair_length,
            hair_type=dao.hair_type,
            history_preferences=dao.history_preferences,
            stripe_customer_id=dao.stripe_customer_id,
            created_at=dao.created_at,
            updated_at=dao.updated_at,
        )

    @staticmethod
    def model_to_dto(model: ClientModel) -> ClientResponseDTO:
        return ClientResponseDTO(
            id=model.id,
            user_account_id=model.user_account_id,
            last_name=model.last_name,
            first_name=model.first_name,
            phone=model.phone,
            gender=model.gender,
            hair_length=model.hair_length,
            hair_type=model.hair_type,
            history_preferences=model.history_preferences,
            stripe_customer_id=model.stripe_customer_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
