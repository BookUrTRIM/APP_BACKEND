from daos.notification_dao import NotificationDAO
from models.notification_model import NotificationModel
from dtos.notification.notification_response_dto import NotificationResponseDTO


class NotificationMapper:
    @staticmethod
    def dao_to_model(dao: NotificationDAO) -> NotificationModel:
        return NotificationModel(
            id=dao.id,
            appointment_id=dao.appointment_id,
            recipient=dao.recipient,
            notification_type=dao.notification_type,
            sent_at=dao.sent_at,
            status=dao.status,
        )

    @staticmethod
    def model_to_dto(model: NotificationModel) -> NotificationResponseDTO:
        return NotificationResponseDTO(
            id=model.id,
            appointment_id=model.appointment_id,
            recipient=model.recipient,
            notification_type=model.notification_type,
            sent_at=model.sent_at,
            status=model.status,
        )
