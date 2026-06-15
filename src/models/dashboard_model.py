from dataclasses import dataclass
from typing import List

@dataclass
class MonthlyStatModel:
    month: str
    realized_revenue: float
    completed_appointments: int
    cancelled_appointments: int

@dataclass
class DashboardModel:
    booked_appointments: int
    completed_appointments: int
    cancellation_rate: float
    expected_revenue: float
    realized_revenue: float
    top_service_name: str
    average_rating: float
    monthly_stats: List[MonthlyStatModel]