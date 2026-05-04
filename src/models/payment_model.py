from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from enums.payment_enum import PaymentStatus, PaymentType


@dataclass
class PaymentModel:
    id: int

    appointment_id: int
    amount: Decimal
    currency: str           
    payment_type: PaymentType
    status: PaymentStatus
    paid_at: Optional[datetime]     

    stripe_payment_intent_id: Optional[str]
    stripe_charge_id: Optional[str]
    stripe_metadata: Optional[dict[str, Any]]
