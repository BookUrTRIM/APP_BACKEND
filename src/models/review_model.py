from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ReviewModel:
    id: int

    appointment_id: int
    rating: int             
    comment: Optional[str]
    reviewed_at: datetime
