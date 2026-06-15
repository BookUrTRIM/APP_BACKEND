from collections import Counter

from sqlalchemy import func
from sqlalchemy.orm import Session

from daos.appointment_dao import AppointmentDAO
from daos.appointment_service_dao import AppointmentServiceDAO
from daos.review_dao import ReviewDAO
from daos.service_dao import ServiceDAO


class DashboardRepository:

    @staticmethod
    def get_all_appointments(db: Session, provider_id: int):
        return db.query(AppointmentDAO).filter(AppointmentDAO.provider_id == provider_id).all()

    @staticmethod
    def get_all_appointment_services(db: Session, provider_id: int):
        return (
            db.query(AppointmentServiceDAO)
            .join(AppointmentDAO)
            .filter(AppointmentDAO.provider_id == provider_id)
            .all()
        )

    @staticmethod
    def get_top_service_name(db: Session, appointment_ids: set) -> str:
        if not appointment_ids:
            return "Aucun"
        services_sold = db.query(AppointmentServiceDAO).filter(AppointmentServiceDAO.appointment_id.in_(appointment_ids)).all()
        service_counts = Counter(s.service_id for s in services_sold)
        if service_counts:
            top_service_id = service_counts.most_common(1)[0][0]
            top_service_obj = db.query(ServiceDAO).filter(ServiceDAO.id == top_service_id).first()
            if top_service_obj:
                return top_service_obj.name
        return "Aucun"

    @staticmethod
    def get_average_rating(db: Session, provider_id: int) -> float:
        return (
            db.query(func.avg(ReviewDAO.rating))
            .join(AppointmentDAO)
            .filter(AppointmentDAO.provider_id == provider_id)
            .scalar() or 0.0
        )
