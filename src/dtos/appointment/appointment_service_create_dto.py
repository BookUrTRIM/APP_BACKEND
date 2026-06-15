from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class AppointmentServiceCreateDTO(BaseModel):
    service_id: int
    adjusted_duration: Optional[int] = Field(None, gt=0, description="Override in minutes; None uses default_duration")
    billed_price: Decimal = Field(ge=0, decimal_places=2)
