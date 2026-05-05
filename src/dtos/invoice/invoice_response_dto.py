from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class InvoiceResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    appointment_id: int
    issued_at: datetime
    total_amount: Decimal
    pdf_url: Optional[str]
