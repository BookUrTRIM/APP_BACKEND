from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class AppointmentServiceModel:
    appointment_id: int
    service_id: int

    adjusted_duration: Optional[int]  
    billed_price: Decimal
