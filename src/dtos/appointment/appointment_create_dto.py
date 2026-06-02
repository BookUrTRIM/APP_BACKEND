from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class AppointmentAnswerDTO(BaseModel):
    question:      str
    answer:        str
    extra_minutes: int


class AppointmentCreateDTO(BaseModel):
    provider_id:      int
    service_id:       Optional[int]                    = None
    start_at:         datetime
    end_at:           datetime
    specific_request: Optional[str]                    = Field(None, max_length=2000)
    answers:          Optional[List[AppointmentAnswerDTO]] = None

    @model_validator(mode='after')
    def check_dates(self) -> 'AppointmentCreateDTO':
        if self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        return self
