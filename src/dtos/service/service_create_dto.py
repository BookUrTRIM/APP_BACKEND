from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ServiceCreateDTO(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    default_duration: int = Field(gt=0, description="Duration in minutes")
    base_price: Decimal = Field(ge=0, decimal_places=2)
