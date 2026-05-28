from dataclasses import dataclass, field
from typing import List


@dataclass
class ServiceQuestionModel:
    id:         int
    service_id: int
    question:   str
    options:    List[dict] = field(default_factory=list)
    order:      int = 0
