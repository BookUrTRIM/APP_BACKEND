from pydantic import BaseModel

from enums.user_enum import UserRole


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
