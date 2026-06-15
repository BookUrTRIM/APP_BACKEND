from datetime import datetime

from pydantic import BaseModel

from enums.user_enum import UserRole


class UserAccountResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
