from http import HTTPStatus
from pathlib import Path

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from dtos.service.service_create_dto import ServiceCreateDTO
from dtos.service.service_update_dto import ServiceUpdateDTO
from services.service_service import ServiceService
from shared.decorators import require_json, safe_swag_from

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs" / "services"
services_bp = Blueprint("services", __name__, url_prefix="/services")


@safe_swag_from(DOCS_DIR / "show.yaml")
@services_bp.get("/<int:service_id>")
def services_show(service_id: int):
    dto = ServiceService.get(service_id)
    return jsonify(dto.model_dump()), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "create.yaml")
@services_bp.post("")
@jwt_required()
@require_json
def services_create():
    user_account_id = int(get_jwt_identity())
    dto = ServiceCreateDTO.model_validate(request.get_json())
    result = ServiceService.create(user_account_id, dto)
    return jsonify(result.model_dump()), HTTPStatus.CREATED


@safe_swag_from(DOCS_DIR / "update.yaml")
@services_bp.patch("/<int:service_id>")
@jwt_required()
@require_json
def services_update(service_id: int):
    user_account_id = int(get_jwt_identity())
    dto = ServiceUpdateDTO.model_validate(request.get_json())
    result = ServiceService.update(service_id, user_account_id, dto)
    return jsonify(result.model_dump()), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "delete.yaml")
@services_bp.delete("/<int:service_id>")
@jwt_required()
def services_delete(service_id: int):
    user_account_id = int(get_jwt_identity())
    ServiceService.delete(service_id, user_account_id)
    return jsonify({}), HTTPStatus.NO_CONTENT
