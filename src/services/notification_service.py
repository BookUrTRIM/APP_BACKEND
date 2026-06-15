import logging
from typing import List

from sqlalchemy.orm import Session

from dtos.notification.notification_response_dto import NotificationResponseDTO
from enums.notification_enum import NotificationStatus, NotificationType, RecipientType
from exceptions.notification_exceptions import NotificationDispatchFailed, NotificationNotFound
from mappers.notification_mapper import NotificationMapper
from repositories.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def send(db: Session, appointment_id: int, recipient: RecipientType, notification_type: NotificationType) -> NotificationResponseDTO:
        notification = NotificationRepository.create(db, appointment_id, recipient, notification_type)

        try:
            NotificationService._dispatch(notification)
            notification = NotificationRepository.update_status(db, notification.id, NotificationStatus.SENT)
            db.commit()
        except Exception as exc:
            logger.error("Échec d'envoi de la notification id=%d : %s", notification.id, exc)
            NotificationRepository.update_status(db, notification.id, NotificationStatus.FAILED)
            db.commit()
            raise NotificationDispatchFailed()

        logger.info("Notification envoyée : id=%d type=%s recipient=%s", notification.id, notification_type, recipient)
        return NotificationMapper.model_to_dto(notification)

    @staticmethod
    def list_by_appointment(db: Session, appointment_id: int) -> List[NotificationResponseDTO]:
        notifications = NotificationRepository.list_by_appointment(db, appointment_id)
        return [NotificationMapper.model_to_dto(n) for n in notifications]

    @staticmethod
    def _dispatch(notification) -> None:
        pass
