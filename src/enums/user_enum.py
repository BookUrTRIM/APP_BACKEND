from enum import Enum


class UserRole(str, Enum):
    CLIENT   = 'client'
    PROVIDER = 'provider'
