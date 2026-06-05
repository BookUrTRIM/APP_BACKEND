from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ServiceUpdateDTO(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    default_duration: Optional[int] = Field(None, gt=0)
    base_price: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    deposit_amount: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
