from typing import List, Optional

from daos.notification_dao import NotificationDAO
from enums.notification_enum import NotificationStatus, NotificationType, RecipientType
from mappers.notification_mapper import NotificationMapper
from models.notification_model import NotificationModel
from shared.db import get_db_session


class NotificationRepository:
    @staticmethod
    def create(
        appointment_id: int,
        recipient: RecipientType,
        notification_type: NotificationType,
    ) -> NotificationModel:
        session = get_db_session()

        dao = NotificationDAO(
            appointment_id=appointment_id,
            recipient=recipient,
            notification_type=notification_type,
        )
        session.add(dao)
        session.commit()
        session.refresh(dao)
        return NotificationMapper.dao_to_model(dao)

    @staticmethod
    def update_status(notification_id: int, status: NotificationStatus) -> Optional[NotificationModel]:
        session = get_db_session()
        dao = session.get(NotificationDAO, notification_id)
        if not dao:
            return None

        dao.status = status
        session.commit()
        session.refresh(dao)
        return NotificationMapper.dao_to_model(dao)

    @staticmethod
    def list_by_appointment(appointment_id: int) -> List[NotificationModel]:
        session = get_db_session()
        rows = (
            session.query(NotificationDAO)
            .where(NotificationDAO.appointment_id == appointment_id)
            .order_by(NotificationDAO.sent_at.desc())
            .all()
        )
        return [NotificationMapper.dao_to_model(row) for row in rows]
