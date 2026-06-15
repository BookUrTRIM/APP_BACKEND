from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReviewResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    appointment_id: int
    rating: int
    comment: Optional[str]
    reviewed_at: datetime
