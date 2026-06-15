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
    business_name: Optional[str] = None
    address: Optional[str] = None
    stripe_account_id: Optional[str] = None
    is_single_tenant: bool = False
    created_at: datetime
    updated_at: datetime
