from typing import Optional

from pydantic import BaseModel, Field


class ProviderCreateDTO(BaseModel):
    last_name: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
