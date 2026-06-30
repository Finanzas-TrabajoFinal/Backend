from enum import Enum


class Moneda(str, Enum):
    PEN = "PEN"
    USD = "USD"


class TipoTasa(str, Enum):
    TNA = "TNA"
    TEA = "TEA"


class Capitalizacion(str, Enum):
    DIARIA = "DIARIA"
    MENSUAL = "MENSUAL"
    BIMESTRAL = "BIMESTRAL"
    TRIMESTRAL = "TRIMESTRAL"
    SEMESTRAL = "SEMESTRAL"
    ANUAL = "ANUAL"


class TipoGracia(str, Enum):
    TOTAL = "T"
    PARCIAL = "P"
    SIN_GRACIA = "S"
