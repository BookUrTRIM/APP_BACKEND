from typing import List, Optional

from pydantic import BaseModel, Field

from dtos.service.service_question_create_dto import QuestionOption


class ServiceQuestionUpdateDTO(BaseModel):
    question: Optional[str]              = None
    options:  Optional[List[QuestionOption]] = None
    order:    Optional[int]              = Field(default=None, ge=0)
