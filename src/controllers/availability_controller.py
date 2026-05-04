from http import HTTPStatus
from pathlib import Path

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from dtos.availability.availability_create_dto import AvailabilityCreateDTO
from dtos.availability.availability_update_dto import AvailabilityUpdateDTO
from services.availability_service import AvailabilityService
from shared.decorators import require_json, safe_swag_from

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs" / "availabilities"
availabilities_bp = Blueprint("availabilities", __name__, url_prefix="/availabilities")


@safe_swag_from(DOCS_DIR / "create.yaml")
@availabilities_bp.post("")
@jwt_required()
@require_json
def availabilities_create():
    user_account_id = int(get_jwt_identity())
    dto = AvailabilityCreateDTO.model_validate(request.get_json())
    result = AvailabilityService.create(user_account_id, dto)
    return jsonify(result.model_dump()), HTTPStatus.CREATED


@safe_swag_from(DOCS_DIR / "update.yaml")
@availabilities_bp.patch("/<int:availability_id>")
@jwt_required()
@require_json
def availabilities_update(availability_id: int):
    user_account_id = int(get_jwt_identity())
    dto = AvailabilityUpdateDTO.model_validate(request.get_json())
    result = AvailabilityService.update(availability_id, user_account_id, dto)
    return jsonify(result.model_dump()), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "delete.yaml")
@availabilities_bp.delete("/<int:availability_id>")
@jwt_required()
def availabilities_delete(availability_id: int):
    user_account_id = int(get_jwt_identity())
    AvailabilityService.delete(availability_id, user_account_id)
    return jsonify({}), HTTPStatus.NO_CONTENT
