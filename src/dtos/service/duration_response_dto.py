from pydantic import BaseModel


class DurationResponseDTO(BaseModel):
    duration: int
