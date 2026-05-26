import logging
from typing import List

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request

import config
from dtos.payment.payment_create_dto import PaymentCreateDTO
from dtos.payment.payment_intent_response_dto import PaymentIntentResponseDTO
from dtos.payment.payment_response_dto import PaymentResponseDTO
from services.payment_service import PaymentService
from shared.dependencies import get_current_user

payments_router = APIRouter(prefix="/payments", tags=["payments"])
logger = logging.getLogger(__name__)


@payments_router.post("", status_code=201, response_model=PaymentResponseDTO)
def payments_create(dto: PaymentCreateDTO, current_user: dict = Depends(get_current_user)):
    return PaymentService.initiate(dto)


@payments_router.get("/{payment_id}", response_model=PaymentResponseDTO)
def payments_show(payment_id: int, current_user: dict = Depends(get_current_user)):
    return PaymentService.get(payment_id)


@payments_router.get("/appointment/{appointment_id}", response_model=List[PaymentResponseDTO])
def payments_by_appointment(appointment_id: int, current_user: dict = Depends(get_current_user)):
    return PaymentService.list_by_appointment(appointment_id)


@payments_router.post("/{payment_id}/prepare", response_model=PaymentIntentResponseDTO)
def payments_prepare(payment_id: int, current_user: dict = Depends(get_current_user)):
    return PaymentService.prepare(payment_id)


@payments_router.post("/webhook")
async def payments_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Endpoint Stripe webhook — pas de JWT, signature vérifiée via STRIPE_WEBHOOK_SECRET.
    """
    payload = await request.body()
    event = _verify_stripe_signature(payload, stripe_signature or "")

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type == "payment_intent.succeeded":
        pi_id = data.get("id")
        charge_id = data.get("latest_charge")
        metadata = data.get("metadata")
        PaymentService.confirm_webhook(pi_id, charge_id, metadata)
        logger.info("Webhook traité : payment_intent.succeeded pi=%s", pi_id)

    elif event_type == "payment_intent.payment_failed":
        pi_id = data.get("id")
        PaymentService.fail_webhook(pi_id)
        logger.info("Webhook traité : payment_intent.payment_failed pi=%s", pi_id)

    elif event_type == "charge.refunded":
        charge_id = data.get("id")
        PaymentService.refund_webhook(charge_id)
        logger.info("Webhook traité : charge.refunded charge=%s", charge_id)

    return {"received": True}


def _verify_stripe_signature(payload: bytes, sig_header: str) -> dict:
    if not config.STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET non configuré.")
        raise HTTPException(status_code=500, detail="Configuration Stripe manquante.")
    try:
        return stripe.Webhook.construct_event(payload, sig_header, config.STRIPE_WEBHOOK_SECRET)
    except stripe.SignatureVerificationError as e:
        logger.warning("Signature Stripe invalide : %s", e)
        raise HTTPException(status_code=400, detail="Signature Stripe invalide.")
    except Exception as e:
        logger.error("Erreur inattendue lors de la vérification Stripe : %s", e)
        raise HTTPException(status_code=400, detail="Payload Stripe invalide.")
