from daos.user_account_dao import UserAccountDAO
from models.user_account_model import UserAccountModel
from dtos.auth.user_account_response_dto import UserAccountResponseDTO


class UserAccountMapper:
    @staticmethod
    def dao_to_model(dao: UserAccountDAO) -> UserAccountModel:
        return UserAccountModel(
            id=dao.id,
            email=dao.email,
            password_hash=dao.password_hash,
            role=dao.role,
            is_active=dao.is_active,
            created_at=dao.created_at,
            updated_at=dao.updated_at,
        )

    @staticmethod
    def model_to_dto(model: UserAccountModel) -> UserAccountResponseDTO:
        return UserAccountResponseDTO(
            id=model.id,
            email=model.email,
            role=model.role,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
