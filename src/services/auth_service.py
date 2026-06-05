import logging
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from sqlalchemy.orm import Session

import config
from dtos.auth.login_dto import LoginDTO
from dtos.auth.signup_dto import SignupDTO
from dtos.auth.user_account_response_dto import UserAccountResponseDTO
from dtos.client.client_create_dto import ClientCreateDTO
from dtos.provider.provider_create_dto import ProviderCreateDTO
from enums.user_enum import UserRole
from exceptions.auth_exceptions import InvalidCredentials, InvalidVerificationToken
from exceptions.user_account_exceptions import EmailAlreadyExists, UserAccountDeactivated
from mappers.user_account_mapper import UserAccountMapper
from repositories.client_repository import ClientRepository
from repositories.provider_repository import ProviderRepository
from repositories.user_account_repository import UserAccountRepository
from services.email_service import EmailService

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def signup(db: Session, dto: SignupDTO) -> UserAccountResponseDTO:
        if UserAccountRepository.get_by_email(db, dto.email):
            raise EmailAlreadyExists()
        password_hash = bcrypt.hashpw(dto.password.encode(), bcrypt.gensalt()).decode()
        account = UserAccountRepository.create(db, dto, password_hash)
        AuthService._create_profile(db, account.id, dto)
        verification_token = jwt.encode(
            {
                "sub": account.email,
                "type": "verify_email",
                "exp": datetime.now(timezone.utc) + timedelta(hours=24),
            },
            config.JWT_SECRET_KEY,
            algorithm="HS256",
        )
        EmailService.send_verification_email(account.email, verification_token)
        db.commit()
        logger.info("Nouveau compte créé (en attente de validation) : id=%d role=%s", account.id, account.role)
        return UserAccountMapper.model_to_dto(account)

    @staticmethod
    def _create_profile(db: Session, user_account_id: int, dto: SignupDTO) -> None:
        if dto.role == UserRole.CLIENT:
            ClientRepository.create(
                db,
                ClientCreateDTO(first_name=dto.first_name, last_name=dto.last_name, phone=dto.phone),
                user_account_id,
            )
        elif dto.role == UserRole.PROVIDER:
            ProviderRepository.create(
                db,
                ProviderCreateDTO(first_name=dto.first_name, last_name=dto.last_name, phone=dto.phone),
                user_account_id,
            )

    @staticmethod
    def login(db: Session, dto: LoginDTO) -> dict:
        account = UserAccountRepository.get_by_email(db, dto.email)
        if not account or not bcrypt.checkpw(dto.password.encode(), account.password_hash.encode()):
            raise InvalidCredentials()
        if not account.is_active:
            raise UserAccountDeactivated()
        token = jwt.encode(
            {
                "sub": str(account.id),
                "email": account.email,
                "role": account.role.value,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=config.JWT_ACCESS_TOKEN_TTL_MINUTES),
            },
            config.JWT_SECRET_KEY,
            algorithm="HS256",
        )
        logger.info("Connexion réussie : id=%d role=%s", account.id, account.role)
        return {"access_token": token, "token_type": "bearer", "role": account.role.value}

    @staticmethod
    def verify_email(db: Session, token: str) -> dict:
        try:
            payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])
            if payload.get("type") != "verify_email":
                raise InvalidVerificationToken()
            email = payload.get("sub")
        except jwt.PyJWTError:
            raise InvalidVerificationToken()

        account = UserAccountRepository.get_by_email(db, email)
        if not account:
            raise InvalidVerificationToken()
        if account.is_active:
            return {"message": "Compte déjà activé."}
        UserAccountRepository.activate_user(db, account.id)
        db.commit()
        logger.info("Compte activé suite à la vérification d'email : id=%d", account.id)
        return {"message": "Email vérifié avec succès."}