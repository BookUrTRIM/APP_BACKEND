from enum import Enum


class HairType(str, Enum):
    LISSE        = 'lisse'
    ONDULE       = 'ondulé'
    BOUCLE       = 'bouclé'
    CREPU_FIN    = 'crépu fin'
    CREPU_EPAIS  = 'crépu épais'


class HairLength(str, Enum):
    COURT      = 'court'
    MI_LONG    = 'mi-long'
    LONG       = 'long'
    TRES_LONG  = 'très long'
