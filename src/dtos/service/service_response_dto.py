from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class ServiceResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    provider_id: int
    name: str
    description: Optional[str]
    default_duration: int
    base_price: Decimal
    deposit_amount: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
