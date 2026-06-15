from typing import List, Optional

from sqlalchemy.orm import Session

from daos.notification_dao import NotificationDAO
from enums.notification_enum import NotificationStatus, NotificationType, RecipientType
from mappers.notification_mapper import NotificationMapper
from models.notification_model import NotificationModel


class NotificationRepository:
    @staticmethod
    def create(db: Session, appointment_id: int, recipient: RecipientType, notification_type: NotificationType) -> NotificationModel:
        dao = NotificationDAO(
            appointment_id=appointment_id,
            recipient=recipient,
            notification_type=notification_type,
        )
        db.add(dao)
        db.flush()
        db.refresh(dao)
        return NotificationMapper.dao_to_model(dao)

    @staticmethod
    def update_status(db: Session, notification_id: int, status: NotificationStatus) -> Optional[NotificationModel]:
        dao = db.get(NotificationDAO, notification_id)
        if not dao:
            return None
        dao.status = status
        db.flush()
        db.refresh(dao)
        return NotificationMapper.dao_to_model(dao)

    @staticmethod
    def list_by_appointment(db: Session, appointment_id: int) -> List[NotificationModel]:
        rows = (
            db.query(NotificationDAO)
            .where(NotificationDAO.appointment_id == appointment_id)
            .order_by(NotificationDAO.sent_at.desc())
            .all()
        )
        return [NotificationMapper.dao_to_model(row) for row in rows]
