import logging
from http import HTTPStatus
from pathlib import Path

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from dtos.payment.payment_create_dto import PaymentCreateDTO
from services.payment_service import PaymentService
from shared.decorators import require_json, safe_swag_from

DOCS_DIR = Path(__file__).resolve().parents[1] / "docs" / "payments"
payments_bp = Blueprint("payments", __name__, url_prefix="/payments")
logger = logging.getLogger(__name__)


@safe_swag_from(DOCS_DIR / "create.yaml")
@payments_bp.post("")
@jwt_required()
@require_json
def payments_create():
    dto = PaymentCreateDTO.model_validate(request.get_json())
    result = PaymentService.initiate(dto)
    return jsonify(result.model_dump()), HTTPStatus.CREATED


@safe_swag_from(DOCS_DIR / "show.yaml")
@payments_bp.get("/<int:payment_id>")
@jwt_required()
def payments_show(payment_id: int):
    result = PaymentService.get(payment_id)
    return jsonify(result.model_dump()), HTTPStatus.OK


@safe_swag_from(DOCS_DIR / "appointment_list.yaml")
@payments_bp.get("/appointment/<int:appointment_id>")
@jwt_required()
def payments_by_appointment(appointment_id: int):
    items = PaymentService.list_by_appointment(appointment_id)
    return jsonify([it.model_dump() for it in items]), HTTPStatus.OK


@payments_bp.post("/webhook")
def payments_webhook():
    """
    Endpoint Stripe webhook — pas de JWT, signature vérifiée via STRIPE_WEBHOOK_SECRET.
    Stripe envoie un POST avec l'en-tête Stripe-Signature.
    """
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature", "")

    event = _verify_stripe_signature(payload, sig_header)
    if event is None:
        return jsonify({"error": "Signature invalide."}), HTTPStatus.BAD_REQUEST

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type == "payment_intent.succeeded":
        pi_id = data.get("id")
        charge_id = data.get("latest_charge")
        metadata = data.get("metadata")
        PaymentService.confirm_webhook(pi_id, charge_id, metadata)
        logger.info("Webhook traité : payment_intent.succeeded pi=%s", pi_id)

    return jsonify({"received": True}), HTTPStatus.OK


def _verify_stripe_signature(payload: str, sig_header: str) -> dict | None:
    """
    Vérifie la signature Stripe. Retourne l'event parsé ou None si invalide.
    Nécessite STRIPE_WEBHOOK_SECRET dans l'environnement et la lib stripe.
    """
    import os
    try:
        import stripe
        webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET"]
        return stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ImportError, Exception) as e:
        logger.warning("Vérification Stripe ignorée : %s", e)
        return None
