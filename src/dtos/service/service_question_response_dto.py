from typing import List

from pydantic import BaseModel

from dtos.service.service_question_create_dto import QuestionOption


class ServiceQuestionResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    id:         int
    service_id: int
    question:   str
    options:    List[QuestionOption]
    order:      int
