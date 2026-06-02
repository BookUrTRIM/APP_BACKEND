from datetime import datetime, timedelta
from models.dashboard_model import DashboardModel, MonthlyStatModel
from repositories.dashboard_repository import DashboardRepository
from repositories.provider_repository import ProviderRepository
from exceptions.provider_exceptions import ProviderNotFound


class DashboardService:
    @staticmethod
    def get_metrics(user_account_id: int, period: str) -> DashboardModel:
        provider = ProviderRepository.get_by_user_account_id(user_account_id)
        if not provider:
            raise ProviderNotFound()
        now = datetime.utcnow()
        if period == "week":
            start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = (start_date + timedelta(days=6)).replace(hour=23, minute=59, second=59, microsecond=999999)
        elif period == "year":
            start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        elif period.isdigit() and len(period) == 4:
            y = int(period)
            start_date = datetime(y, 1, 1, 0, 0, 0)
            end_date = datetime(y, 12, 31, 23, 59, 59)
        else:
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
            end_date = (next_month - timedelta(seconds=1))
        appts = DashboardRepository.get_all_appointments(provider.id)
        services_sold = DashboardRepository.get_all_appointment_services(provider.id)
        appt_revenues = {}
        for s in services_sold:
            appt_revenues[s.appointment_id] = appt_revenues.get(s.appointment_id, 0) + float(s.billed_price)
        filtered_appts = []
        for a in appts:
            if a.start_at:
                if start_date <= a.start_at.replace(tzinfo=None) <= end_date:
                    filtered_appts.append(a)
        confirmed_appts = [a for a in filtered_appts if a.status.value == 'confirmed']
        completed_appts = [a for a in filtered_appts if a.status.value == 'completed']
        cancelled_appts = [a for a in filtered_appts if a.status.value == 'cancelled']
        total_filtered = len(filtered_appts)
        total_booked_count = len(confirmed_appts) + len(completed_appts)
        expected_revenue = sum(appt_revenues.get(a.id, 0) for a in confirmed_appts)
        realized_revenue = sum(appt_revenues.get(a.id, 0) for a in completed_appts)
        total_cancel_rate = (len(cancelled_appts) / total_filtered * 100) if total_filtered > 0 else 0.0
        filtered_appt_ids = {a.id for a in filtered_appts}
        top_service_name = DashboardRepository.get_top_service_name(filtered_appt_ids)
        avg_rating = DashboardRepository.get_average_rating(provider.id)
        monthly_stats = []
        mois_fr = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        for i in range(5, -1, -1):
            target_month = now.month - i
            target_year = now.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            month_label = f"{mois_fr[target_month - 1]} {target_year}"
            month_appts = [a for a in appts if
                           a.start_at and a.start_at.replace(tzinfo=None).month == target_month and a.start_at.replace(
                               tzinfo=None).year == target_year]
            m_completed = [a for a in month_appts if a.status.value == 'completed']
            m_cancelled = [a for a in month_appts if a.status.value == 'cancelled']
            m_revenue = sum(appt_revenues.get(a.id, 0) for a in m_completed)
            monthly_stats.append(MonthlyStatModel(
                month=month_label,
                realized_revenue=m_revenue,
                completed_appointments=len(m_completed),
                cancelled_appointments=len(m_cancelled)
            ))

        return DashboardModel(
            booked_appointments=total_booked_count,
            completed_appointments=len(completed_appts),
            cancellation_rate=round(total_cancel_rate, 1),
            expected_revenue=expected_revenue,
            realized_revenue=realized_revenue,
            top_service_name=top_service_name,
            average_rating=round(avg_rating, 1),
            monthly_stats=monthly_stats
        )