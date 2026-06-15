from models.dashboard_model import DashboardModel
from dtos.dashboard.dashboard_dto import DashboardResponseDTO, MonthlyStatDTO

class DashboardMapper:
    @staticmethod
    def model_to_dto(model: DashboardModel) -> DashboardResponseDTO:
        return DashboardResponseDTO(
            booked_appointments=model.booked_appointments,
            completed_appointments=model.completed_appointments,
            cancellation_rate=model.cancellation_rate,
            expected_revenue=model.expected_revenue,
            realized_revenue=model.realized_revenue,
            top_service_name=model.top_service_name,
            average_rating=model.average_rating,
            monthly_stats=[
                MonthlyStatDTO(
                    month=m.month,
                    realized_revenue=m.realized_revenue,
                    completed_appointments=m.completed_appointments,
                    cancelled_appointments=m.cancelled_appointments
                ) for m in model.monthly_stats
            ]
        )