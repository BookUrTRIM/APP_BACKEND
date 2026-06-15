from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ClientModel:
    id: int

    user_account_id: int
    last_name: str
    first_name: str
    phone: Optional[str]

    gender: Optional[str]
    hair_length: Optional[str]
    hair_type: Optional[str]
    history_preferences: Optional[str]

    stripe_customer_id: Optional[str]

    created_at: datetime
    updated_at: datetime
