"""
Orquestador del motor financiero.
Recibe un SimulacionInput (Pydantic) y devuelve un CronogramaResult.
No importa nada de FastAPI ni SQLAlchemy.
"""
from decimal import Decimal
from dataclasses import dataclass

from app.domain.rates import resolver_tasas
from app.domain.schedule import construir_cronograma, FilaCronograma
from app.domain.indicators import (
    calcular_van,
    calcular_tir,
    tir_a_tcea,
    cok_anual_a_mensual,
)


@dataclass
class CabeceraCronograma:
    tea: Decimal
    tem: Decimal
    cuota_inicial: Decimal
    cuota_final: Decimal
    monto_prestamo: Decimal
    saldo_regular: Decimal
    cuota_regular: Decimal
    tir_mensual: Decimal
    tcea: Decimal
    van: Decimal


@dataclass
class CronogramaResult:
    cabecera: CabeceraCronograma
    cronograma: list[FilaCronograma]


def simular(inp) -> CronogramaResult:
    """
    inp: app.schemas.cotizacion.SimulacionInput (o cualquier objeto con los mismos campos)
    """
    # 1. Tasas
    tea, tem = resolver_tasas(
        tasa_valor=Decimal(str(inp.tasa_valor)),
        tasa_tipo=inp.tasa_tipo,
        capitalizacion=inp.capitalizacion,
        frecuencia_dias=inp.frecuencia_dias,
        dias_anio=inp.dias_anio,
    )

    # 2. Montos cabecera
    pv = Decimal(str(inp.precio_venta))
    ci = pv * Decimal(str(inp.pct_cuota_inicial))
    cf = pv * Decimal(str(inp.pct_cuota_final))
    costes_ini = sum(Decimal(str(v)) for v in inp.costes_iniciales.values())
    prestamo = (pv - ci) + costes_ini

    # 3. Costos periódicos
    cp = inp.costes_periodicos
    pct_desg = Decimal(str(cp.get("pct_seg_desgravamen", 0)))
    # Seguro de riesgo vehicular: tasa anual sobre precio_venta, prorrateada al período
    pct_riesgo = Decimal(str(cp.get("pct_seg_riesgo", 0)))
    periodos_por_anio = Decimal(str(inp.dias_anio)) / Decimal(str(inp.frecuencia_dias))
    seg_riesgo = pct_riesgo * pv / periodos_por_anio
    gps = Decimal(str(cp.get("gps", 0)))
    portes = Decimal(str(cp.get("portes", 0)))
    gastos_adm = Decimal(str(cp.get("gastos_adm", 0)))

    # 4. Gracia
    gracia = inp.gracia or {}
    gracia_total = int(gracia.get("total", 0))
    gracia_parcial = int(gracia.get("parcial", 0))

    # 5. Cronograma
    saldo_regular, cuota_regular, filas = construir_cronograma(
        monto_prestamo=prestamo,
        cf=cf,
        tem=tem,
        pct_seg_desgravamen=pct_desg,
        seg_riesgo=seg_riesgo,
        gps=gps,
        portes=portes,
        gastos_adm=gastos_adm,
        num_cuotas=inp.num_cuotas,
        gracia_total=gracia_total,
        gracia_parcial=gracia_parcial,
    )

    # 6. Vector de flujo para TIR/VAN
    # Período 0: el deudor recibe el préstamo neto (precio - CI - costes iniciales no financiados)
    # Según el Excel: flujo_0 = +préstamo (el desembolso del banco)
    flujos: list[Decimal] = [prestamo] + [f.flujo for f in filas]

    tir_m = calcular_tir(flujos)
    tcea = tir_a_tcea(tir_m)
    cok_m = cok_anual_a_mensual(Decimal(str(inp.cok_anual)))
    van = calcular_van(flujos, cok_m)

    cabecera = CabeceraCronograma(
        tea=tea,
        tem=tem,
        cuota_inicial=ci,
        cuota_final=cf,
        monto_prestamo=prestamo,
        saldo_regular=saldo_regular,
        cuota_regular=cuota_regular,
        tir_mensual=tir_m,
        tcea=tcea,
        van=van,
    )

    return CronogramaResult(cabecera=cabecera, cronograma=filas)
