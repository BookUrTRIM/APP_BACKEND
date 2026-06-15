from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dtos.appointment.appointment_create_dto import AppointmentCreateDTO
from dtos.appointment.appointment_response_dto import AppointmentResponseDTO
from dtos.appointment.appointment_update_dto import AppointmentUpdateDTO
from dtos.invoice.invoice_response_dto import InvoiceResponseDTO
from dtos.receipt.receipt_response_dto import ReceiptResponseDTO
from dtos.review.review_create_dto import ReviewCreateDTO
from dtos.review.review_response_dto import ReviewResponseDTO
from enums.appointment_enum import AppointmentStatus
from enums.user_enum import UserRole
from services.appointment_service import AppointmentService
from services.invoice_service import InvoiceService
from services.receipt_service import ReceiptService
from services.review_service import ReviewService
from shared.db import get_db
from shared.dependencies import get_current_user

appointments_router = APIRouter(prefix="/appointments", tags=["appointments"])


@appointments_router.get("/client", response_model=dict)
def appointments_client_list(
    status: Optional[AppointmentStatus] = None,
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items, total = AppointmentService.list_by_client(db, int(current_user["sub"]), status=status, page=page, limit=limit)
    return {"items": items, "total": total, "page": page, "limit": limit}


@appointments_router.get("/provider", response_model=dict)
def appointments_provider_list(
    status: Optional[AppointmentStatus] = None,
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    items, total = AppointmentService.list_by_provider(db, int(current_user["sub"]), status=status, page=page, limit=limit)
    return {"items": items, "total": total, "page": page, "limit": limit}


@appointments_router.get("/{appointment_id}", response_model=AppointmentResponseDTO)
def appointments_show(appointment_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> AppointmentResponseDTO:
    return AppointmentService.get(db, appointment_id, int(current_user["sub"]), UserRole(current_user["role"]))


@appointments_router.post("", status_code=201, response_model=AppointmentResponseDTO)
def appointments_create(dto: AppointmentCreateDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> AppointmentResponseDTO:
    return AppointmentService.book(db, int(current_user["sub"]), dto)


@appointments_router.patch("/{appointment_id}", response_model=AppointmentResponseDTO)
def appointments_update(appointment_id: int, dto: AppointmentUpdateDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> AppointmentResponseDTO:
    return AppointmentService.update(db, appointment_id, int(current_user["sub"]), UserRole(current_user["role"]), dto)


@appointments_router.post("/{appointment_id}/complete", response_model=AppointmentResponseDTO)
def appointments_complete(appointment_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> AppointmentResponseDTO:
    return AppointmentService.complete(db, appointment_id, int(current_user["sub"]))


@appointments_router.post("/{appointment_id}/cancel", response_model=AppointmentResponseDTO)
def appointments_cancel(appointment_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> AppointmentResponseDTO:
    return AppointmentService.cancel(db, appointment_id, int(current_user["sub"]), UserRole(current_user["role"]))


@appointments_router.post("/{appointment_id}/cancel-by-client", response_model=AppointmentResponseDTO)
def appointments_cancel_by_client(appointment_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> AppointmentResponseDTO:
    return AppointmentService.cancel_by_client(db, appointment_id, int(current_user["sub"]))


@appointments_router.post("/{appointment_id}/cancel-by-provider", response_model=AppointmentResponseDTO)
def appointments_cancel_by_provider(appointment_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> AppointmentResponseDTO:
    return AppointmentService.cancel_by_provider(db, appointment_id, int(current_user["sub"]))


# ── Reçus ─────────────────────────────────────────────────────────────────

@appointments_router.get("/{appointment_id}/receipts", response_model=List[ReceiptResponseDTO])
def appointments_receipts_list(appointment_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> List[ReceiptResponseDTO]:
    return ReceiptService.list_by_appointment(db, appointment_id, int(current_user["sub"]), UserRole(current_user["role"]))


# ── Facture ────────────────────────────────────────────────────────────────

@appointments_router.post("/{appointment_id}/invoice", status_code=201, response_model=InvoiceResponseDTO)
def appointments_invoice_generate(appointment_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> InvoiceResponseDTO:
    return InvoiceService.generate(db, appointment_id, int(current_user["sub"]), UserRole(current_user["role"]))


@appointments_router.get("/{appointment_id}/invoice", response_model=InvoiceResponseDTO)
def appointments_invoice_show(appointment_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> InvoiceResponseDTO:
    return InvoiceService.get_by_appointment(db, appointment_id, int(current_user["sub"]), UserRole(current_user["role"]))


# ── Avis ───────────────────────────────────────────────────────────────────

@appointments_router.post("/{appointment_id}/review", status_code=201, response_model=ReviewResponseDTO)
def appointments_review_create(appointment_id: int, dto: ReviewCreateDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ReviewResponseDTO:
    dto.appointment_id = appointment_id
    return ReviewService.create(db, int(current_user["sub"]), dto)


@appointments_router.get("/{appointment_id}/review", response_model=ReviewResponseDTO)
def appointments_review_show(appointment_id: int, db: Session = Depends(get_db)) -> ReviewResponseDTO:
    return ReviewService.get_by_appointment(db, appointment_id)
