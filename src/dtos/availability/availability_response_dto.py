from datetime import date, datetime, time

from pydantic import BaseModel

from enums.availability_enum import AvailabilityType


class AvailabilityResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    provider_id: int
    day_date: date
    start_time: time
    end_time: time
    slot_type: AvailabilityType
    created_at: datetime
    updated_at: datetime
