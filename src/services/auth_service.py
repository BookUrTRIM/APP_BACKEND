import logging

import bcrypt

from dtos.auth.signup_dto import SignupDTO
from dtos.auth.user_account_response_dto import UserAccountResponseDTO
from exceptions.auth_exceptions import InvalidCredentials
from exceptions.user_account_exceptions import EmailAlreadyExists, UserAccountDeactivated
from mappers.user_account_mapper import UserAccountMapper
from models.user_account_model import UserAccountModel
from repositories.user_account_repository import UserAccountRepository

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def signup(dto: SignupDTO) -> UserAccountResponseDTO:
        if UserAccountRepository.get_by_email(dto.email):
            raise EmailAlreadyExists()

        password_hash = bcrypt.hashpw(dto.password.encode(), bcrypt.gensalt()).decode()
        account = UserAccountRepository.create(dto, password_hash)
        logger.info("Nouveau compte créé : id=%d role=%s", account.id, account.role)
        return UserAccountMapper.model_to_dto(account)

    @staticmethod
    def login(dto) -> UserAccountModel:
        """Vérifie les credentials et retourne le model. Le token JWT est créé par le controller."""
        account = UserAccountRepository.get_by_email(dto.email)
        if not account or not bcrypt.checkpw(dto.password.encode(), account.password_hash.encode()):
            raise InvalidCredentials()
        if not account.is_active:
            raise UserAccountDeactivated()
        return account
