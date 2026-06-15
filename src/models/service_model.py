from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class ServiceModel:
    id: int

    provider_id: int
    name: str
    description: Optional[str]

    default_duration: int
    base_price: Decimal
    deposit_amount: Optional[Decimal]

    created_at: datetime
    updated_at: datetime
