from typing import Optional

from sqlalchemy.orm import Session

from daos.user_account_dao import UserAccountDAO
from dtos.auth.signup_dto import SignupDTO
from mappers.user_account_mapper import UserAccountMapper
from models.user_account_model import UserAccountModel


class UserAccountRepository:
    @staticmethod
    def create(db: Session, dto: SignupDTO, password_hash: str) -> UserAccountModel:
        dao = UserAccountDAO(
            email=dto.email,
            password_hash=password_hash,
            role=dto.role,
            is_active=False
        )
        db.add(dao)
        db.flush()
        db.refresh(dao)
        return UserAccountMapper.dao_to_model(dao)

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[UserAccountModel]:
        dao = db.get(UserAccountDAO, user_id)
        return UserAccountMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[UserAccountModel]:
        dao = db.query(UserAccountDAO).where(UserAccountDAO.email == email).first()
        return UserAccountMapper.dao_to_model(dao) if dao else None

    @staticmethod
    def set_active(db: Session, user_id: int, is_active: bool) -> Optional[UserAccountModel]:
        dao = db.get(UserAccountDAO, user_id)
        if not dao:
            return None
        dao.is_active = is_active
        db.flush()
        db.refresh(dao)
        return UserAccountMapper.dao_to_model(dao)

    @staticmethod
    def activate_user(db: Session, user_id: int) -> None:
        UserAccountRepository.set_active(db, user_id, True)