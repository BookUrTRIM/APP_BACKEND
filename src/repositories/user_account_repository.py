from typing import Optional

from daos.user_account_dao import UserAccountDAO
from dtos.auth.signup_dto import SignupDTO
from mappers.user_account_mapper import UserAccountMapper
from models.user_account_model import UserAccountModel
from shared.db import get_db_session


class UserAccountRepository:
    @staticmethod
    def create(dto: SignupDTO, password_hash: str) -> UserAccountModel:
        with get_db_session() as session:
            dao = UserAccountDAO(
                email=dto.email,
                password_hash=password_hash,
                role=dto.role,
            )
            session.add(dao)
            session.commit()
            session.refresh(dao)
            return UserAccountMapper.dao_to_model(dao)

    @staticmethod
    def get_by_id(user_id: int) -> Optional[UserAccountModel]:
        with get_db_session() as session:
            dao = session.get(UserAccountDAO, user_id)
            return UserAccountMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def get_by_email(email: str) -> Optional[UserAccountModel]:
        with get_db_session() as session:
            dao = session.query(UserAccountDAO).where(UserAccountDAO.email == email).first()
            return UserAccountMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def set_active(user_id: int, is_active: bool) -> Optional[UserAccountModel]:
        with get_db_session() as session:
            dao = session.get(UserAccountDAO, user_id)
            if not dao:
                return None
            dao.is_active = is_active
            session.commit()
            session.refresh(dao)
            return UserAccountMapper.dao_to_model(dao)
