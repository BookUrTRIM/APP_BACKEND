from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class AppointmentServiceResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    appointment_id: int
    service_id: int
    adjusted_duration: Optional[int]
    billed_price: Decimal
