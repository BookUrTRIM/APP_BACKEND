from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from enums.user_enum import UserRole


class SignupDTO(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: UserRole
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
