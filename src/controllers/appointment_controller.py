from http import HTTPStatus
from pathlib import Path

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from dtos.appointment.appointment_create_dto import AppointmentCreateDTO
from dtos.appointment.appointment_update_dto import AppointmentUpdateDTO
from enums.appointment_enum import AppointmentStatus
from enums.user_enum import UserRole
from services.appointment_service import AppointmentService
from services.invoice_service import InvoiceService
from services.review_service import ReviewService
from shared.decorators import require_json, safe_swag_from

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs" / "appointments"
appointments_bp = Blueprint("appointments", __name__, url_prefix="/appointments")


@safe_swag_from(DOCS_DIR / "client_list.yaml")
@appointments_bp.get("/client")
@jwt_required()
def appointments_client_list():
    user_account_id = int(get_jwt_identity())
    status_str = request.args.get("status")
    status = AppointmentStatus(status_str) if status_str else None
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))

    items, total = AppointmentService.list_by_client(user_account_id, status=status, page=page, limit=limit)
    return jsonify({
        "items": [it.model_dump() for it in items],
        "total": total,
        "page": page,
        "limit": limit,
    }), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "provider_list.yaml")
@appointments_bp.get("/provider")
@jwt_required()
def appointments_provider_list():
    user_account_id = int(get_jwt_identity())
    status_str = request.args.get("status")
    status = AppointmentStatus(status_str) if status_str else None
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 20))

    items, total = AppointmentService.list_by_provider(user_account_id, status=status, page=page, limit=limit)
    return jsonify({
        "items": [it.model_dump() for it in items],
        "total": total,
        "page": page,
        "limit": limit,
    }), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "show.yaml")
@appointments_bp.get("/<int:appointment_id>")
@jwt_required()
def appointments_show(appointment_id: int):
    user_account_id = int(get_jwt_identity())
    role = UserRole(get_jwt()["role"])
    dto = AppointmentService.get(appointment_id, user_account_id, role)
    return jsonify(dto.model_dump()), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "create.yaml")
@appointments_bp.post("")
@jwt_required()
@require_json
def appointments_create():
    user_account_id = int(get_jwt_identity())
    dto = AppointmentCreateDTO.model_validate(request.get_json())
    result = AppointmentService.book(user_account_id, dto)
    return jsonify(result.model_dump()), HTTPStatus.CREATED


@safe_swag_from(DOCS_DIR / "update.yaml")
@appointments_bp.patch("/<int:appointment_id>")
@jwt_required()
@require_json
def appointments_update(appointment_id: int):
    user_account_id = int(get_jwt_identity())
    role = UserRole(get_jwt()["role"])
    dto = AppointmentUpdateDTO.model_validate(request.get_json())
    result = AppointmentService.update(appointment_id, user_account_id, role, dto)
    return jsonify(result.model_dump()), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "cancel.yaml")
@appointments_bp.post("/<int:appointment_id>/cancel")
@jwt_required()
def appointments_cancel(appointment_id: int):
    user_account_id = int(get_jwt_identity())
    role = UserRole(get_jwt()["role"])
    result = AppointmentService.cancel(appointment_id, user_account_id, role)
    return jsonify(result.model_dump()), HTTPStatus.OK


# ── Facture ────────────────────────────────────────────────────────────────

@safe_swag_from(DOCS_DIR / "invoice_generate.yaml")
@appointments_bp.post("/<int:appointment_id>/invoice")
@jwt_required()
def appointments_invoice_generate(appointment_id: int):
    result = InvoiceService.generate(appointment_id)
    return jsonify(result.model_dump()), HTTPStatus.CREATED


@safe_swag_from(DOCS_DIR / "invoice_show.yaml")
@appointments_bp.get("/<int:appointment_id>/invoice")
@jwt_required()
def appointments_invoice_show(appointment_id: int):
    result = InvoiceService.get_by_appointment(appointment_id)
    return jsonify(result.model_dump()), HTTPStatus.OK


# ── Avis ───────────────────────────────────────────────────────────────────

@safe_swag_from(DOCS_DIR / "review_create.yaml")
@appointments_bp.post("/<int:appointment_id>/review")
@jwt_required()
@require_json
def appointments_review_create(appointment_id: int):
    from dtos.review.review_create_dto import ReviewCreateDTO
    user_account_id = int(get_jwt_identity())
    body = request.get_json()
    body["appointment_id"] = appointment_id
    dto = ReviewCreateDTO.model_validate(body)
    result = ReviewService.create(user_account_id, dto)
    return jsonify(result.model_dump()), HTTPStatus.CREATED


@safe_swag_from(DOCS_DIR / "review_show.yaml")
@appointments_bp.get("/<int:appointment_id>/review")
def appointments_review_show(appointment_id: int):
    result = ReviewService.get_by_appointment(appointment_id)
    return jsonify(result.model_dump()), HTTPStatus.OK
