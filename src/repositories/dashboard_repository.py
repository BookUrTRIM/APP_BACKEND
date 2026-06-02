from collections import Counter
from sqlalchemy import func
from shared.db import get_db_session
from daos.appointment_dao import AppointmentDAO
from daos.appointment_service_dao import AppointmentServiceDAO
from daos.service_dao import ServiceDAO
from daos.review_dao import ReviewDAO


class DashboardRepository:

    @staticmethod
    def get_all_appointments(provider_id: int):
        session = get_db_session()
        return session.query(AppointmentDAO).filter(AppointmentDAO.provider_id == provider_id).all()

    @staticmethod
    def get_all_appointment_services(provider_id: int):
        session = get_db_session()
        return session.query(AppointmentServiceDAO) \
            .join(AppointmentDAO) \
            .filter(AppointmentDAO.provider_id == provider_id).all()

    @staticmethod
    def get_top_service_name(appointment_ids: set) -> str:
        session = get_db_session()
        if not appointment_ids:
            return "Aucun"
        services_sold = session.query(AppointmentServiceDAO) \
            .filter(AppointmentServiceDAO.appointment_id.in_(appointment_ids)).all()
        service_counts = Counter(s.service_id for s in services_sold)
        if service_counts:
            top_service_id = service_counts.most_common(1)[0][0]
            top_service_obj = session.query(ServiceDAO).filter(ServiceDAO.id == top_service_id).first()
            if top_service_obj:
                return top_service_obj.name
        return "Aucun"

    @staticmethod
    def get_average_rating(provider_id: int) -> float:
        session = get_db_session()
        return session.query(func.avg(ReviewDAO.rating)) \
            .join(AppointmentDAO).filter(AppointmentDAO.provider_id == provider_id).scalar() or 0.0