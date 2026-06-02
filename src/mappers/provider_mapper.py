from daos.provider_dao import ProviderDAO
from models.provider_model import ProviderModel
from dtos.provider.provider_response_dto import ProviderResponseDTO


class ProviderMapper:
    @staticmethod
    def dao_to_model(dao: ProviderDAO) -> ProviderModel:
        return ProviderModel(
            id=dao.id,
            user_account_id=dao.user_account_id,
            last_name=dao.last_name,
            first_name=dao.first_name,
            phone=dao.phone,
            business_name=dao.business_name,
            address=dao.address,
            google_calendar_token_enc=dao.google_calendar_token_enc,
            stripe_account_id=dao.stripe_account_id,
            created_at=dao.created_at,
            updated_at=dao.updated_at,
        )

    @staticmethod
    def model_to_dto(model: ProviderModel) -> ProviderResponseDTO:
        return ProviderResponseDTO(
            id=model.id,
            user_account_id=model.user_account_id,
            last_name=model.last_name,
            first_name=model.first_name,
            phone=model.phone,
            business_name=model.business_name,
            address=model.address,
            stripe_account_id=model.stripe_account_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
