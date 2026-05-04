from http import HTTPStatus
from pathlib import Path

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from dtos.auth.login_dto import LoginDTO
from dtos.auth.signup_dto import SignupDTO
from services.auth_service import AuthService
from shared.decorators import require_json, safe_swag_from

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs" / "auth"
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@safe_swag_from(DOCS_DIR / "signup.yaml")
@auth_bp.post("/signup")
@require_json
def auth_signup():
    dto = SignupDTO.model_validate(request.get_json())
    account = AuthService.signup(dto)
    return jsonify(account.model_dump()), HTTPStatus.CREATED


@safe_swag_from(DOCS_DIR / "login.yaml")
@auth_bp.post("/login")
@require_json
def auth_login():
    dto = LoginDTO.model_validate(request.get_json())
    account = AuthService.login(dto)
    token = create_access_token(
        identity=str(account.id),
        additional_claims={"role": account.role.value},
    )
    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "role": account.role.value,
    }), HTTPStatus.OK
