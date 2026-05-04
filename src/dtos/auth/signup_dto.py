from pydantic import BaseModel, EmailStr, Field

from enums.user_enum import UserRole


class SignupDTO(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole
