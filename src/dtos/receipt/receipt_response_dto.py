from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from enums.payment_enum import PaymentType


class ReceiptResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    payment_id: int
    appointment_id: int
    amount: Decimal
    currency: str
    payment_type: PaymentType
    issued_at: datetime
    stripe_receipt_url: Optional[str] = None
