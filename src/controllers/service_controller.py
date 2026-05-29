from typing import List

from fastapi import APIRouter, Depends, Response

from dtos.service.duration_calculate_dto import DurationCalculateDTO
from dtos.service.duration_response_dto import DurationResponseDTO
from dtos.service.service_create_dto import ServiceCreateDTO
from dtos.service.service_question_create_dto import ServiceQuestionCreateDTO
from dtos.service.service_question_response_dto import ServiceQuestionResponseDTO
from dtos.service.service_question_update_dto import ServiceQuestionUpdateDTO
from dtos.service.service_response_dto import ServiceResponseDTO
from dtos.service.service_update_dto import ServiceUpdateDTO
from services.service_question_service import ServiceQuestionService
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


# ── Questions ──────────────────────────────────────────────────────────────

@services_router.post("/{service_id}/calculate-duration", response_model=DurationResponseDTO)
def services_calculate_duration(service_id: int, dto: DurationCalculateDTO):
    return ServiceQuestionService.calculate_duration(service_id, dto)


@services_router.get("/{service_id}/questions", response_model=List[ServiceQuestionResponseDTO])
def questions_list(service_id: int):
    return ServiceQuestionService.list(service_id)


@services_router.post("/{service_id}/questions", status_code=201, response_model=ServiceQuestionResponseDTO)
def questions_create(
    service_id: int,
    dto: ServiceQuestionCreateDTO,
    current_user: dict = Depends(get_current_user),
):
    return ServiceQuestionService.create(service_id, int(current_user["sub"]), dto)


@services_router.put("/questions/{question_id}", response_model=ServiceQuestionResponseDTO)
def questions_update(
    question_id: int,
    dto: ServiceQuestionUpdateDTO,
    current_user: dict = Depends(get_current_user),
):
    return ServiceQuestionService.update(question_id, int(current_user["sub"]), dto)


@services_router.delete("/questions/{question_id}", status_code=204)
def questions_delete(question_id: int, current_user: dict = Depends(get_current_user)):
    ServiceQuestionService.delete(question_id, int(current_user["sub"]))
    return Response(status_code=204)
