from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dtos.notification.notification_response_dto import NotificationResponseDTO
from enums.notification_enum import NotificationStatus, NotificationType, RecipientType
from exceptions.notification_exceptions import NotificationNotFound
from mappers.notification_mapper import NotificationMapper
from repositories.notification_repository import NotificationRepository
from services.notification_service import NotificationService
from shared.db import get_db
from shared.dependencies import get_current_user

notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])


@notifications_router.get(
    "/appointment/{appointment_id}",
    response_model=List[NotificationResponseDTO],
)
def notifications_by_appointment(
    appointment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[NotificationResponseDTO]:
    return NotificationService.list_by_appointment(db, appointment_id)


@notifications_router.post(
    "/appointment/{appointment_id}",
    status_code=201,
    response_model=NotificationResponseDTO,
)
def notifications_send(
    appointment_id: int,
    recipient: RecipientType,
    notification_type: NotificationType,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationResponseDTO:
    return NotificationService.send(db, appointment_id, recipient, notification_type)


@notifications_router.patch(
    "/{notification_id}/status",
    response_model=NotificationResponseDTO,
)
def notifications_update_status(
    notification_id: int,
    status: NotificationStatus,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NotificationResponseDTO:
    notification = NotificationRepository.update_status(db, notification_id, status)
    if not notification:
        raise NotificationNotFound()
    db.commit()
    return NotificationMapper.model_to_dto(notification)
