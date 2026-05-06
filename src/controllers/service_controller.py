from fastapi import APIRouter, Depends, Response

from dtos.service.service_create_dto import ServiceCreateDTO
from dtos.service.service_response_dto import ServiceResponseDTO
from dtos.service.service_update_dto import ServiceUpdateDTO
from services.service_service import ServiceService
from shared.dependencies import get_current_user

services_router = APIRouter(prefix="/services", tags=["services"])


@services_router.get("/{service_id}", response_model=ServiceResponseDTO)
def services_show(service_id: int):
    return ServiceService.get(service_id)


@services_router.post("", status_code=201, response_model=ServiceResponseDTO)
def services_create(dto: ServiceCreateDTO, current_user: dict = Depends(get_current_user)):
    return ServiceService.create(int(current_user["sub"]), dto)


@services_router.patch("/{service_id}", response_model=ServiceResponseDTO)
def services_update(
    service_id: int,
    dto: ServiceUpdateDTO,
    current_user: dict = Depends(get_current_user),
):
    return ServiceService.update(service_id, int(current_user["sub"]), dto)


@services_router.delete("/{service_id}", status_code=204)
def services_delete(service_id: int, current_user: dict = Depends(get_current_user)):
    ServiceService.delete(service_id, int(current_user["sub"]))
    return Response(status_code=204)
