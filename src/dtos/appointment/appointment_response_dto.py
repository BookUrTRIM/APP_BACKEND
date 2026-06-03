from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from enums.appointment_enum import AppointmentStatus


class AppointmentResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    client_id: int
    provider_id: int
    start_at: datetime
    end_at: datetime
    status: AppointmentStatus
    products_used: Optional[str]
    specific_request: Optional[str]
    answers: Optional[List[dict]] = None
    deposit_amount: Optional[float] = None
    service_name: Optional[str] = None
    service_base_price: Optional[float] = None
    created_at: datetime
    updated_at: datetime
