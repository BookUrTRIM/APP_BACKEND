from typing import Optional

from pydantic import BaseModel, Field


class ClientCreateDTO(BaseModel):
    last_name: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    gender: Optional[str] = Field(None, max_length=50)
    hair_length: Optional[str] = Field(None, max_length=50)
    hair_type: Optional[str] = Field(None, max_length=50)
    history_preferences: Optional[str] = None
