from typing import Optional

from pydantic import BaseModel, Field


class ReviewCreateDTO(BaseModel):
    appointment_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)
