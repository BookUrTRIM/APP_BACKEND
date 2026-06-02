from sqlalchemy import func
from datetime import datetime
from shared.db import get_db_session
from daos.appointment_dao import AppointmentDAO
from daos.appointment_service_dao import AppointmentServiceDAO
from daos.service_dao import ServiceDAO
from daos.review_dao import ReviewDAO
from daos.provider_dao import ProviderDAO


class DashboardRepository:
    @staticmethod
    def get_provider_dashboard_metrics(user_account_id: int):
        session = get_db_session()
        provider = session.query(ProviderDAO).filter(ProviderDAO.user_account_id == user_account_id).first()
        if not provider:
            return None
        provider_id = provider.id
        appts = session.query(AppointmentDAO).filter(AppointmentDAO.provider_id == provider_id).all()
        appt_revenues = {}
        services_sold = session.query(AppointmentServiceDAO).join(AppointmentDAO).filter(
            AppointmentDAO.provider_id == provider_id).all()
        for s in services_sold:
            appt_revenues[s.appointment_id] = appt_revenues.get(s.appointment_id, 0) + float(s.billed_price)
        total_appts = len(appts)
        booked = [a for a in appts if a.status.value in ['pending', 'confirmed']]
        completed = [a for a in appts if a.status.value == 'completed']
        cancelled = [a for a in appts if a.status.value == 'cancelled']
        expected_revenue = sum(appt_revenues.get(a.id, 0) for a in booked)
        realized_revenue = sum(appt_revenues.get(a.id, 0) for a in completed)
        top_service = session.query(ServiceDAO.name, func.count(AppointmentServiceDAO.service_id).label('count')) \
            .join(AppointmentServiceDAO) \
            .join(AppointmentDAO) \
            .filter(AppointmentDAO.provider_id == provider_id) \
            .group_by(ServiceDAO.name).order_by(func.count(AppointmentServiceDAO.service_id).desc()).first()
        avg_rating = session.query(func.avg(ReviewDAO.rating)) \
                         .join(AppointmentDAO) \
                         .filter(AppointmentDAO.provider_id == provider_id).scalar() or 0.0

        total_cancel_rate = (len(cancelled) / total_appts * 100) if total_appts > 0 else 0.0
        monthly_stats = []
        now = datetime.now()
        mois_fr = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        for i in range(5, -1, -1):
            target_month = now.month - i
            target_year = now.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            month_label = f"{mois_fr[target_month - 1]} {target_year}"
            month_appts = [a for a in appts if a.start_at.month == target_month and a.start_at.year == target_year]
            m_total = len(month_appts)
            m_completed = [a for a in month_appts if a.status.value == 'completed']
            m_cancelled = [a for a in month_appts if a.status.value == 'cancelled']
            m_revenue = sum(appt_revenues.get(a.id, 0) for a in m_completed)
            m_cancel_rate = (len(m_cancelled) / m_total * 100) if m_total > 0 else 0.0
            monthly_stats.append({
                "month": month_label,
                "realized_revenue": m_revenue,
                "completed_appointments": len(m_completed),
                "cancellation_rate": round(m_cancel_rate, 1)
            })

        return {
            "booked_appointments": len(booked),
            "completed_appointments": len(completed),
            "cancellation_rate": round(total_cancel_rate, 1),
            "expected_revenue": expected_revenue,
            "realized_revenue": realized_revenue,
            "top_service_name": top_service.name if top_service else "Aucun",
            "average_rating": round(avg_rating, 1),
            "monthly_stats": monthly_stats
        }