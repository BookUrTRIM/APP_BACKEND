from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends

from dtos.provider.provider_create_dto import ProviderCreateDTO
from dtos.provider.provider_response_dto import ProviderResponseDTO
from dtos.provider.provider_update_dto import ProviderUpdateDTO
from services.availability_service import AvailabilityService
from services.provider_service import ProviderService
from services.review_service import ReviewService
from services.service_service import ServiceService
from shared.dependencies import get_current_user

providers_router = APIRouter(prefix="/providers", tags=["providers"])


@providers_router.get("", response_model=dict)
def providers_index(page: int = 1, limit: int = 20):
    items, total = ProviderService.list(page=page, limit=limit)
    return {"items": items, "total": total, "page": page, "limit": limit}


@providers_router.get("/me", response_model=ProviderResponseDTO)
def providers_me(current_user: dict = Depends(get_current_user)):
    return ProviderService.get_me(int(current_user["sub"]))


@providers_router.patch("/me", response_model=ProviderResponseDTO)
def providers_update_me(dto: ProviderUpdateDTO, current_user: dict = Depends(get_current_user)):
    provider = ProviderService.get_me(int(current_user["sub"]))
    return ProviderService.update(provider.id, int(current_user["sub"]), dto)


@providers_router.get("/{provider_id}", response_model=ProviderResponseDTO)
def providers_show(provider_id: int):
    return ProviderService.get(provider_id)


@providers_router.post("", status_code=201, response_model=ProviderResponseDTO)
def providers_create(dto: ProviderCreateDTO, current_user: dict = Depends(get_current_user)):
    return ProviderService.create(int(current_user["sub"]), dto)


@providers_router.patch("/{provider_id}", response_model=ProviderResponseDTO)
def providers_update(
    provider_id: int,
    dto: ProviderUpdateDTO,
    current_user: dict = Depends(get_current_user),
):
    return ProviderService.update(provider_id, int(current_user["sub"]), dto)


@providers_router.get("/{provider_id}/services", response_model=dict)
def providers_services(provider_id: int, page: int = 1, limit: int = 20):
    items, total = ServiceService.list_by_provider(provider_id, page=page, limit=limit)
    return {"items": items, "total": total, "page": page, "limit": limit}


@providers_router.get("/{provider_id}/availabilities")
def providers_availabilities(provider_id: int, date: Optional[date] = None):
    return AvailabilityService.list_by_provider(provider_id, day_date=date)


@providers_router.get("/{provider_id}/reviews", response_model=dict)
def providers_reviews(provider_id: int, page: int = 1, limit: int = 20):
    items, total = ReviewService.list_by_provider(provider_id, page=page, limit=limit)
    return {"items": items, "total": total, "page": page, "limit": limit}
