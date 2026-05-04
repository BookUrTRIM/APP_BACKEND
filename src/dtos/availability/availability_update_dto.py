from datetime import date, time
from typing import Optional

from pydantic import BaseModel

from enums.availability_enum import AvailabilityType


class AvailabilityUpdateDTO(BaseModel):
    day_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_type: Optional[AvailabilityType] = None
