from pydantic import BaseModel
from typing import List

class MonthlyStatDTO(BaseModel):
    month: str
    realized_revenue: float
    completed_appointments: int
    cancellation_rate: float

class DashboardResponseDTO(BaseModel):
    booked_appointments: int
    completed_appointments: int
    cancellation_rate: float
    expected_revenue: float
    realized_revenue: float
    top_service_name: str
    average_rating: float
    monthly_stats: List[MonthlyStatDTO]