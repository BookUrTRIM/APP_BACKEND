from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dtos.client.client_create_dto import ClientCreateDTO
from dtos.client.client_response_dto import ClientResponseDTO
from dtos.client.client_update_dto import ClientUpdateDTO
from dtos.client.hair_profile_response_dto import HairProfileResponseDTO
from dtos.client.hair_profile_upsert_dto import HairProfileUpsertDTO
from services.client_service import ClientService
from shared.db import get_db
from shared.dependencies import get_current_user

clients_router = APIRouter(prefix="/clients", tags=["clients"])


@clients_router.get("/me", response_model=ClientResponseDTO)
def clients_me(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ClientResponseDTO:
    return ClientService.get_me(db, int(current_user["sub"]))


@clients_router.get("/me/hair-profile", response_model=Optional[HairProfileResponseDTO])
def clients_hair_profile_get(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> Optional[HairProfileResponseDTO]:
    return ClientService.get_hair_profile(db, int(current_user["sub"]))


@clients_router.put("/me/hair-profile", response_model=HairProfileResponseDTO)
def clients_hair_profile_upsert(dto: HairProfileUpsertDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> HairProfileResponseDTO:
    return ClientService.upsert_hair_profile(db, int(current_user["sub"]), dto)


@clients_router.patch("/me", response_model=ClientResponseDTO)
def clients_update_me(dto: ClientUpdateDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ClientResponseDTO:
    client = ClientService.get_me(db, int(current_user["sub"]))
    return ClientService.update(db, client.id, int(current_user["sub"]), dto)


@clients_router.get("/{client_id}", response_model=ClientResponseDTO)
def clients_show(client_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ClientResponseDTO:
    return ClientService.get(db, client_id)


@clients_router.post("", status_code=201, response_model=ClientResponseDTO)
def clients_create(dto: ClientCreateDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ClientResponseDTO:
    return ClientService.create(db, int(current_user["sub"]), dto)


@clients_router.patch("/{client_id}", response_model=ClientResponseDTO)
def clients_update(client_id: int, dto: ClientUpdateDTO, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)) -> ClientResponseDTO:
    return ClientService.update(db, client_id, int(current_user["sub"]), dto)
