from pydantic import BaseModel

from enums.hair_enum import HairLength, HairType


class HairProfileUpsertDTO(BaseModel):
    hair_type:   HairType
    hair_length: HairLength
