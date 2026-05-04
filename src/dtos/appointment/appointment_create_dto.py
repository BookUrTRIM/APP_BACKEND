from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class AppointmentCreateDTO(BaseModel):
    provider_id: int
    start_at: datetime
    end_at: datetime
    specific_request: Optional[str] = Field(None, max_length=2000)

    @model_validator(mode='after')
    def check_dates(self) -> 'AppointmentCreateDTO':
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self
