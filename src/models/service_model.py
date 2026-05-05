from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class ServiceModel:
    id: int

    provider_id: int
    name: str
    description: str | None

    default_duration: int   
    base_price: Decimal

    created_at: datetime
    updated_at: datetime
