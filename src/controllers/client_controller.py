from http import HTTPStatus
from pathlib import Path

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from dtos.client.client_create_dto import ClientCreateDTO
from dtos.client.client_update_dto import ClientUpdateDTO
from services.client_service import ClientService
from shared.decorators import require_json, safe_swag_from

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs" / "clients"
clients_bp = Blueprint("clients", __name__, url_prefix="/clients")


@safe_swag_from(DOCS_DIR / "me.yaml")
@clients_bp.get("/me")
@jwt_required()
def clients_me():
    user_account_id = int(get_jwt_identity())
    dto = ClientService.get_me(user_account_id)
    return jsonify(dto.model_dump()), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "show.yaml")
@clients_bp.get("/<int:client_id>")
@jwt_required()
def clients_show(client_id: int):
    dto = ClientService.get(client_id)
    return jsonify(dto.model_dump()), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "create.yaml")
@clients_bp.post("")
@jwt_required()
@require_json
def clients_create():
    user_account_id = int(get_jwt_identity())
    dto = ClientCreateDTO.model_validate(request.get_json())
    result = ClientService.create(user_account_id, dto)
    return jsonify(result.model_dump()), HTTPStatus.CREATED


@safe_swag_from(DOCS_DIR / "update.yaml")
@clients_bp.patch("/<int:client_id>")
@jwt_required()
@require_json
def clients_update(client_id: int):
    user_account_id = int(get_jwt_identity())
    dto = ClientUpdateDTO.model_validate(request.get_json())
    result = ClientService.update(client_id, user_account_id, dto)
    return jsonify(result.model_dump()), HTTPStatus.OK
