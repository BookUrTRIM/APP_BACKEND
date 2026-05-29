from pydantic import BaseModel

from enums.hair_enum import HairLength, HairType


class HairProfileResponseDTO(BaseModel):
    model_config = {"from_attributes": True}

    id:          int
    client_id:   int
    hair_type:   HairType
    hair_length: HairLength
