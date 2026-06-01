from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProviderResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_account_id: int
    last_name: str
    first_name: str
    phone: Optional[str]
    stripe_account_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
