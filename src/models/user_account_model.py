from dataclasses import dataclass
from datetime import datetime

from enums.user_enum import UserRole


@dataclass
class UserAccountModel:
    id: int

    email: str
    password_hash: str
    role: UserRole
    is_active: bool

    created_at: datetime
    updated_at: datetime
