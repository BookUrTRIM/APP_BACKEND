from typing import List

from pydantic import BaseModel, Field


class AnswerItem(BaseModel):
    question_id:  int
    option_index: int = Field(ge=0)


class DurationCalculateDTO(BaseModel):
    answers: List[AnswerItem]
