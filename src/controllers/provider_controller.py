from http import HTTPStatus
from pathlib import Path

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from dtos.provider.provider_create_dto import ProviderCreateDTO
from dtos.provider.provider_update_dto import ProviderUpdateDTO
from services.provider_service import ProviderService
from services.review_service import ReviewService
from services.service_service import ServiceService
from services.availability_service import AvailabilityService
from shared.decorators import require_json, safe_swag_from

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs" / "providers"
providers_bp = Blueprint("providers", __name__, url_prefix="/providers")


@safe_swag_from(DOCS_DIR / "index.yaml")
@providers_bp.get("")
def providers_index():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    items, total = ProviderService.list(page=page, limit=limit)
    return jsonify({
        "items": [it.model_dump() for it in items],
        "total": total,
        "page": page,
        "limit": limit,
    }), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "me.yaml")
@providers_bp.get("/me")
@jwt_required()
def providers_me():
    user_account_id = int(get_jwt_identity())
    dto = ProviderService.get_me(user_account_id)
    return jsonify(dto.model_dump()), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "show.yaml")
@providers_bp.get("/<int:provider_id>")
def providers_show(provider_id: int):
    dto = ProviderService.get(provider_id)
    return jsonify(dto.model_dump()), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "create.yaml")
@providers_bp.post("")
@jwt_required()
@require_json
def providers_create():
    user_account_id = int(get_jwt_identity())
    dto = ProviderCreateDTO.model_validate(request.get_json())
    result = ProviderService.create(user_account_id, dto)
    return jsonify(result.model_dump()), HTTPStatus.CREATED


@safe_swag_from(DOCS_DIR / "update.yaml")
@providers_bp.patch("/<int:provider_id>")
@jwt_required()
@require_json
def providers_update(provider_id: int):
    user_account_id = int(get_jwt_identity())
    dto = ProviderUpdateDTO.model_validate(request.get_json())
    result = ProviderService.update(provider_id, user_account_id, dto)
    return jsonify(result.model_dump()), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "services.yaml")
@providers_bp.get("/<int:provider_id>/services")
def providers_services(provider_id: int):
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    items, total = ServiceService.list_by_provider(provider_id, page=page, limit=limit)
    return jsonify({
        "items": [it.model_dump() for it in items],
        "total": total,
        "page": page,
        "limit": limit,
    }), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "availabilities.yaml")
@providers_bp.get("/<int:provider_id>/availabilities")
def providers_availabilities(provider_id: int):
    from datetime import date
    day_str = request.args.get("date")
    day_date = date.fromisoformat(day_str) if day_str else None
    items = AvailabilityService.list_by_provider(provider_id, day_date=day_date)
    return jsonify([it.model_dump() for it in items]), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "reviews.yaml")
@providers_bp.get("/<int:provider_id>/reviews")
def providers_reviews(provider_id: int):
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))
    items, total = ReviewService.list_by_provider(provider_id, page=page, limit=limit)
    return jsonify({
        "items": [it.model_dump() for it in items],
        "total": total,
        "page": page,
        "limit": limit,
    }), HTTPStatus.OK
