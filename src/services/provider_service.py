import logging
from typing import List, Tuple

import stripe
from sqlalchemy.orm import Session

import config
from dtos.provider.provider_create_dto import ProviderCreateDTO
from dtos.provider.provider_response_dto import ProviderResponseDTO
from dtos.provider.provider_update_dto import ProviderUpdateDTO
from exceptions.provider_exceptions import (
    ProviderAccessDenied,
    ProviderAlreadyExists,
    ProviderNotFound,
    StripeConnectAlreadyExists,
    StripeConnectNotConfigured,
)
from mappers.provider_mapper import ProviderMapper
from repositories.provider_repository import ProviderRepository

logger = logging.getLogger(__name__)


class ProviderService:
    @staticmethod
    def create(db: Session, user_account_id: int, dto: ProviderCreateDTO) -> ProviderResponseDTO:
        if ProviderRepository.get_by_user_account_id(db, user_account_id):
            raise ProviderAlreadyExists()
        provider = ProviderRepository.create(db, dto, user_account_id)
        db.commit()
        logger.info("Profil prestataire créé : id=%d user_account_id=%d", provider.id, provider.user_account_id)
        return ProviderMapper.model_to_dto(provider)

    @staticmethod
    def update(db: Session, provider_id: int, current_user_account_id: int, dto: ProviderUpdateDTO) -> ProviderResponseDTO:
        provider = ProviderRepository.get_by_id(db, provider_id)
        if not provider:
            raise ProviderNotFound()
        if provider.user_account_id != current_user_account_id:
            raise ProviderAccessDenied()
        updated = ProviderRepository.update(db, provider_id, dto)
        db.commit()
        return ProviderMapper.model_to_dto(updated)

    @staticmethod
    def get(db: Session, provider_id: int) -> ProviderResponseDTO:
        provider = ProviderRepository.get_by_id(db, provider_id)
        if not provider:
            raise ProviderNotFound()
        return ProviderMapper.model_to_dto(provider)

    @staticmethod
    def get_me(db: Session, user_account_id: int) -> ProviderResponseDTO:
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider:
            raise ProviderNotFound()
        return ProviderMapper.model_to_dto(provider)

    @staticmethod
    def list(db: Session, page: int = 1, limit: int = 20) -> Tuple[List[ProviderResponseDTO], int]:
        providers, total = ProviderRepository.list(db, page=page, limit=limit)
        return [ProviderMapper.model_to_dto(p) for p in providers], total

    @staticmethod
    def create_connect_account(db: Session, user_account_id: int) -> ProviderResponseDTO:
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider:
            raise ProviderNotFound()
        if provider.stripe_account_id:
            raise StripeConnectAlreadyExists()

        account = stripe.Account.create(
            type="express",
            country="FR",
            capabilities={
                "card_payments": {"requested": True},
                "transfers": {"requested": True},
            },
        )
        updated = ProviderRepository.set_stripe_account(db, provider.id, account.id)
        db.commit()
        logger.info("Compte Stripe Connect créé : provider_id=%d account=%s", provider.id, account.id)
        return ProviderMapper.model_to_dto(updated)

    @staticmethod
    def get_onboarding_link(db: Session, user_account_id: int) -> str:
        provider = ProviderRepository.get_by_user_account_id(db, user_account_id)
        if not provider:
            raise ProviderNotFound()
        if not provider.stripe_account_id:
            raise StripeConnectNotConfigured()

        link = stripe.AccountLink.create(
            account=provider.stripe_account_id,
            refresh_url=config.STRIPE_CONNECT_REFRESH_URL,
            return_url=config.STRIPE_CONNECT_RETURN_URL,
            type="account_onboarding",
        )
        return link.url
