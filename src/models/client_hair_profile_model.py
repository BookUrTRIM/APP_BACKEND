from dataclasses import dataclass

from enums.hair_enum import HairLength, HairType


@dataclass
class ClientHairProfileModel:
    id:          int
    client_id:   int
    hair_type:   HairType
    hair_length: HairLength
