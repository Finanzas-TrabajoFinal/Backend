from decimal import Decimal, getcontext
from app.domain.enums import TipoTasa, Capitalizacion

getcontext().prec = 28

_PERIODOS_CAP = {
    Capitalizacion.DIARIA: None,       # usa dias_anio como n
    Capitalizacion.MENSUAL: 12,
    Capitalizacion.BIMESTRAL: 6,
    Capitalizacion.TRIMESTRAL: 4,
    Capitalizacion.SEMESTRAL: 2,
    Capitalizacion.ANUAL: 1,
}


def tna_a_tea(tna: Decimal, capitalizacion: Capitalizacion, dias_anio: int) -> Decimal:
    """Convierte TNA a TEA según la capitalización."""
    if capitalizacion == Capitalizacion.DIARIA:
        n = Decimal(dias_anio)
    else:
        n = Decimal(_PERIODOS_CAP[capitalizacion])
    return (1 + tna / n) ** n - 1


def tea_a_tem(tea: Decimal, frecuencia_dias: int, dias_anio: int) -> Decimal:
    """Tasa efectiva del período a partir de TEA."""
    exp = Decimal(frecuencia_dias) / Decimal(dias_anio)
    return (1 + tea) ** exp - 1


def resolver_tasas(
    tasa_valor: Decimal,
    tasa_tipo: TipoTasa,
    capitalizacion: Capitalizacion | None,
    frecuencia_dias: int,
    dias_anio: int,
) -> tuple[Decimal, Decimal]:
    """Devuelve (TEA, TEM)."""
    if tasa_tipo == TipoTasa.TNA:
        tea = tna_a_tea(tasa_valor, capitalizacion, dias_anio)
    else:
        tea = tasa_valor
    tem = tea_a_tem(tea, frecuencia_dias, dias_anio)
    return tea, tem
