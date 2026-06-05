from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dtos.auth.login_dto import LoginDTO
from dtos.auth.signup_dto import SignupDTO
from dtos.auth.user_account_response_dto import UserAccountResponseDTO
from services.auth_service import AuthService
from shared.db import get_db

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/signup", status_code=201, response_model=UserAccountResponseDTO)
def auth_signup(dto: SignupDTO, db: Session = Depends(get_db)):
    return AuthService.signup(db, dto)


@auth_router.post("/login")
def auth_login(dto: LoginDTO, db: Session = Depends(get_db)):
    return AuthService.login(db, dto)


@auth_router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    return AuthService.verify_email(db, token)