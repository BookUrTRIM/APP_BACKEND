from typing import List

from pydantic import BaseModel, Field


class QuestionOption(BaseModel):
    label:         str
    extra_minutes: int = Field(ge=0)


class ServiceQuestionCreateDTO(BaseModel):
    question: str
    options:  List[QuestionOption]
    order:    int = Field(default=0, ge=0)
