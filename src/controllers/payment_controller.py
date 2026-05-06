import logging
from typing import Any, List

from fastapi import APIRouter, Depends, Header, HTTPException, Request

from dtos.payment.payment_create_dto import PaymentCreateDTO
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


@payments_router.post("/webhook")
async def payments_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Endpoint Stripe webhook — pas de JWT, signature vérifiée via STRIPE_WEBHOOK_SECRET.
    """
    payload = await request.body()

    event = _verify_stripe_signature(payload, stripe_signature or "")
    if event is None:
        raise HTTPException(status_code=400, detail="Signature Stripe invalide.")

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type == "payment_intent.succeeded":
        pi_id = data.get("id")
        charge_id = data.get("latest_charge")
        metadata = data.get("metadata")
        PaymentService.confirm_webhook(pi_id, charge_id, metadata)
        logger.info("Webhook traité : payment_intent.succeeded pi=%s", pi_id)

    return {"received": True}


def _verify_stripe_signature(payload: bytes, sig_header: str) -> dict | None:
    import os
    try:
        import stripe
        webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET"]
        return stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ImportError, Exception) as e:
        logger.warning("Vérification Stripe ignorée : %s", e)
        return None
