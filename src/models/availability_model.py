from dataclasses import dataclass
from datetime import date, datetime, time

from enums.availability_enum import AvailabilityType


@dataclass
class AvailabilityModel:
    id: int

    provider_id: int
    day_date: date
    start_time: time
    end_time: time
    slot_type: AvailabilityType

    created_at: datetime
    updated_at: datetime
