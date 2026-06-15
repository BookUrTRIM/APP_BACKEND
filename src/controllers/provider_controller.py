from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dtos.availability.availability_response_dto import AvailabilityResponseDTO
from dtos.provider.provider_create_dto import ProviderCreateDTO
from dtos.provider.provider_response_dto import ProviderResponseDTO
from dtos.provider.provider_update_dto import ProviderUpdateDTO
from services.availability_service import AvailabilityService
from services.provider_service import ProviderService
from services.review_service import ReviewService
from services.service_service import ServiceService
from shared.db import get_db
from shared.dependencies import get_current_user

providers_router = APIRouter(prefix="/providers", tags=["providers"])


@providers_router.get("", response_model=dict)
def providers_index(page: int = 1, limit: int = 20, db: Session = Depends(get_db)) -> dict:
    items, total = ProviderService.list(db, page=page, limit=limit)
    return {"items": items, "total": total, "page": page, "limit": limit}


@providers_router.get("/me", response_model=ProviderResponseDTO)
def providers_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ProviderResponseDTO:
    return ProviderService.get_me(db, int(current_user["sub"]))


@providers_router.patch("/me", response_model=ProviderResponseDTO)
def providers_update_me(dto: ProviderUpdateDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ProviderResponseDTO:
    provider = ProviderService.get_me(db, int(current_user["sub"]))
    return ProviderService.update(db, provider.id, int(current_user["sub"]), dto)


@providers_router.get("/{provider_id}", response_model=ProviderResponseDTO)
def providers_show(provider_id: int, db: Session = Depends(get_db)) -> ProviderResponseDTO:
    return ProviderService.get(db, provider_id)


@providers_router.post("", status_code=201, response_model=ProviderResponseDTO)
def providers_create(dto: ProviderCreateDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ProviderResponseDTO:
    return ProviderService.create(db, int(current_user["sub"]), dto)


@providers_router.patch("/{provider_id}", response_model=ProviderResponseDTO)
def providers_update(provider_id: int, dto: ProviderUpdateDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ProviderResponseDTO:
    return ProviderService.update(db, provider_id, int(current_user["sub"]), dto)


@providers_router.get("/{provider_id}/services", response_model=dict)
def providers_services(provider_id: int, page: int = 1, limit: int = 20, db: Session = Depends(get_db)) -> dict:
    items, total = ServiceService.list_by_provider(db, provider_id, page=page, limit=limit)
    return {"items": items, "total": total, "page": page, "limit": limit}


@providers_router.get("/{provider_id}/availabilities", response_model=List[AvailabilityResponseDTO])
def providers_availabilities(provider_id: int, date: Optional[date] = None, db: Session = Depends(get_db)) -> List[AvailabilityResponseDTO]:
    return AvailabilityService.list_by_provider(db, provider_id, day_date=date)


@providers_router.get("/{provider_id}/reviews", response_model=dict)
def providers_reviews(provider_id: int, page: int = 1, limit: int = 20, db: Session = Depends(get_db)) -> dict:
    items, total = ReviewService.list_by_provider(db, provider_id, page=page, limit=limit)
    return {"items": items, "total": total, "page": page, "limit": limit}


# ── Stripe Connect ─────────────────────────────────────────────────────────

@providers_router.post("/me/stripe-connect", response_model=ProviderResponseDTO)
def providers_stripe_connect_create(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ProviderResponseDTO:
    return ProviderService.create_connect_account(db, int(current_user["sub"]))


@providers_router.get("/me/stripe-connect/onboarding")
def providers_stripe_connect_onboarding(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    url = ProviderService.get_onboarding_link(db, int(current_user["sub"]))
    return {"url": url}
