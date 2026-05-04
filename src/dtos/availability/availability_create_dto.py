from datetime import date, time

from pydantic import BaseModel, model_validator

from enums.availability_enum import AvailabilityType


class AvailabilityCreateDTO(BaseModel):
    day_date: date
    start_time: time
    end_time: time
    slot_type: AvailabilityType = AvailabilityType.WORK

    @model_validator(mode='after')
    def check_time_range(self) -> 'AvailabilityCreateDTO':
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self
