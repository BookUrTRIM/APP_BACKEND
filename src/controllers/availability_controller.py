from typing import List

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from dtos.availability.availability_create_dto import AvailabilityCreateDTO
from dtos.availability.availability_response_dto import AvailabilityResponseDTO
from dtos.availability.availability_update_dto import AvailabilityUpdateDTO
from services.availability_service import AvailabilityService
from shared.db import get_db
from shared.dependencies import get_current_user

availabilities_router = APIRouter(prefix="/availabilities", tags=["availabilities"])


@availabilities_router.post("", status_code=201, response_model=AvailabilityResponseDTO)
def availabilities_create(dto: AvailabilityCreateDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> AvailabilityResponseDTO:
    return AvailabilityService.create(db, int(current_user["sub"]), dto)


@availabilities_router.post("/bulk", status_code=201, response_model=List[AvailabilityResponseDTO])
def availabilities_create_bulk(dtos: List[AvailabilityCreateDTO], current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> List[AvailabilityResponseDTO]:
    return AvailabilityService.create_bulk(db, int(current_user["sub"]), dtos)


@availabilities_router.patch("/{availability_id}", response_model=AvailabilityResponseDTO)
def availabilities_update(availability_id: int, dto: AvailabilityUpdateDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> AvailabilityResponseDTO:
    return AvailabilityService.update(db, availability_id, int(current_user["sub"]), dto)


@availabilities_router.delete("/{availability_id}", status_code=204)
def availabilities_delete(availability_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> Response:
    AvailabilityService.delete(db, availability_id, int(current_user["sub"]))
    return Response(status_code=204)
