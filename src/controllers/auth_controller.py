from fastapi import APIRouter

from dtos.auth.login_dto import LoginDTO
from dtos.auth.signup_dto import SignupDTO
from dtos.auth.user_account_response_dto import UserAccountResponseDTO
from services.auth_service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/signup", status_code=201, response_model=UserAccountResponseDTO)
def auth_signup(dto: SignupDTO):
    return AuthService.signup(dto)


@auth_router.post("/login")
def auth_login(dto: LoginDTO):
    return AuthService.login(dto)
