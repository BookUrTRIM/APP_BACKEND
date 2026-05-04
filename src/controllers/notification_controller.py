from http import HTTPStatus
from pathlib import Path

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from enums.notification_enum import NotificationStatus, NotificationType, RecipientType
from services.notification_service import NotificationService
from shared.decorators import require_json, safe_swag_from

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs" / "notifications"
notifications_bp = Blueprint("notifications", __name__, url_prefix="/notifications")


@safe_swag_from(DOCS_DIR / "appointment_list.yaml")
@notifications_bp.get("/appointment/<int:appointment_id>")
@jwt_required()
def notifications_by_appointment(appointment_id: int):
    items = NotificationService.list_by_appointment(appointment_id)
    return jsonify([it.model_dump() for it in items]), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "send.yaml")
@notifications_bp.post("/appointment/<int:appointment_id>")
@jwt_required()
@require_json
def notifications_send(appointment_id: int):
    body = request.get_json()
    recipient = RecipientType(body["recipient"])
    notification_type = NotificationType(body["notification_type"])
    result = NotificationService.send(appointment_id, recipient, notification_type)
    return jsonify(result.model_dump()), HTTPStatus.CREATED


@safe_swag_from(DOCS_DIR / "update_status.yaml")
@notifications_bp.patch("/<int:notification_id>/status")
@jwt_required()
@require_json
def notifications_update_status(notification_id: int):
    body = request.get_json()
    status = NotificationStatus(body["status"])
    from repositories.notification_repository import NotificationRepository
    from mappers.notification_mapper import NotificationMapper
    notification = NotificationRepository.update_status(notification_id, status)
    if not notification:
        from exceptions.notification_exceptions import NotificationNotFound
        raise NotificationNotFound()
    return jsonify(NotificationMapper.model_to_dto(notification).model_dump()), HTTPStatus.OK
