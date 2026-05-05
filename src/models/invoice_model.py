from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class InvoiceModel:
    id: int

    appointment_id: int
    issued_at: datetime
    total_amount: Decimal
    pdf_url: Optional[str]
