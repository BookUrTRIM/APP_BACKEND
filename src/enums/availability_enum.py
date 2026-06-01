from enum import Enum


class AvailabilityType(str, Enum):
    WORK   = 'work'
    BREAK  = 'break'
    BOOKED = 'booked'
