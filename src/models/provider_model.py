from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ProviderModel:
    id: int

    user_account_id: int
    last_name: str
    first_name: str
    phone: Optional[str]
    business_name: Optional[str]
    address: Optional[str]

    google_calendar_token_enc: Optional[str]
    stripe_account_id: Optional[str]

    created_at: datetime
    updated_at: datetime
