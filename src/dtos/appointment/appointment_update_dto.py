from typing import Optional

from pydantic import BaseModel, Field

from enums.appointment_enum import AppointmentStatus


class AppointmentUpdateDTO(BaseModel):
    status: Optional[AppointmentStatus] = None
    products_used: Optional[str] = Field(None, max_length=2000)
    specific_request: Optional[str] = Field(None, max_length=2000)
