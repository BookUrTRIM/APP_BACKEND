from decimal import Decimal

from pydantic import BaseModel, Field

from enums.payment_enum import PaymentType


class PaymentCreateDTO(BaseModel):
    appointment_id: int
    amount: Decimal = Field(gt=0, decimal_places=2)
    currency: str = Field(default='eur', min_length=3, max_length=3)
    payment_type: PaymentType
