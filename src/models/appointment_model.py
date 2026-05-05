from dataclasses import dataclass
from datetime import datetime
from typing import Optional

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

    created_at: datetime
    updated_at: datetime
