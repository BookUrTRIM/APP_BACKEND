from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from enums.appointment_enum import AppointmentStatus


@dataclass
class AppointmentModel:
    id: int

    client_id: int
    provider_id: int
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus

    products_used: Optional[str]
    specific_request: Optional[str]
    answers: Optional[List[dict]] = field(default=None)
    deposit_amount: Optional[float] = field(default=None)
    service_name: Optional[str] = field(default=None)
    service_base_price: Optional[float] = field(default=None)

    created_at: datetime = field(default=None)
    updated_at: datetime = field(default=None)
