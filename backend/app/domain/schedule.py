"""
Construye el cronograma de pagos con dos saldos paralelos:
  - Saldo del cuotón (CF): solo capitaliza interés + desgravamen; se paga completo al final.
  - Saldo regular: método francés con gracia total/parcial al inicio.

Período extra N+1 = liquidación del cuotón.
"""
from dataclasses import dataclass, field
from decimal import Decimal
from app.domain.enums import TipoGracia


@dataclass
class FilaCuoton:
    saldo_ini: Decimal
    interes: Decimal
    amort: Decimal
    seg_desg: Decimal
    saldo_fin: Decimal


@dataclass
class FilaRegular:
    saldo_ini: Decimal
    interes: Decimal
    cuota: Decimal       # cuota fija (0 en gracia total)
    amort: Decimal
    seg_desg: Decimal
    seg_riesgo: Decimal
    gps: Decimal
    portes: Decimal
    gastos_adm: Decimal
    saldo_fin: Decimal


@dataclass
class FilaCronograma:
    n: int
    pg: TipoGracia
    cuoton: FilaCuoton
    regular: FilaRegular
    flujo: Decimal       # perspectiva deudor (positivo = desembolso recibido, negativo = pago)


def _valor_presente_cuoton(
    cf: Decimal, i_periodo: Decimal, n_total: int
) -> Decimal:
    """VP del cuotón al inicio del préstamo.
    El cuotón se paga en el período N+1 (crece un período más antes de liquidarse),
    por eso se descuenta n_total + 1 períodos.
    """
    return cf / (1 + i_periodo) ** (n_total + 1)


def _cuota_francesa(saldo: Decimal, i: Decimal, n: int) -> Decimal:
    """Cuota fija del método francés."""
    if n == 0:
        return Decimal(0)
    return saldo * i * (1 + i) ** n / ((1 + i) ** n - 1)


def construir_cronograma(
    monto_prestamo: Decimal,
    cf: Decimal,
    tem: Decimal,
    pct_seg_desgravamen: Decimal,
    seg_riesgo: Decimal,
    gps: Decimal,
    portes: Decimal,
    gastos_adm: Decimal,
    num_cuotas: int,
    gracia_total: int,
    gracia_parcial: int,
) -> tuple[Decimal, Decimal, list[FilaCronograma]]:
    """
    Retorna (saldo_regular_inicial, cuota_regular_fija, filas).
    Las filas incluyen el período N+1 de liquidación del cuotón.
    """
    # Tasa del período incluyendo seguro de desgravamen (para annuity francesa)
    i_anualidad = tem + pct_seg_desgravamen

    # Número de cuotas normales (sin gracia)
    n_normal = num_cuotas - gracia_total - gracia_parcial

    # El cuotón ocupa el período N+1 (total num_cuotas + 1 períodos de flujo)
    # Su VP se descuenta al momento 0 a la tasa i_anualidad para num_cuotas períodos
    saldo_cuoton_0 = _valor_presente_cuoton(cf, i_anualidad, num_cuotas)

    saldo_regular_0 = monto_prestamo - saldo_cuoton_0

    # Saldo regular post-gracia total se calcula capitalizando durante gracia total
    saldo_regular_post_gt = saldo_regular_0
    for _ in range(gracia_total):
        saldo_regular_post_gt = saldo_regular_post_gt * (1 + tem)

    # Cuota fija del tramo normal (francés sobre saldo post-gracia-total, descontando gracia parcial)
    # Durante gracia parcial el saldo queda plano (paga solo interés)
    cuota_regular = _cuota_francesa(saldo_regular_post_gt, i_anualidad, n_normal)

    filas: list[FilaCronograma] = []
    saldo_reg = saldo_regular_0
    saldo_cut = saldo_cuoton_0

    for n in range(1, num_cuotas + 1):
        # Tipo de gracia
        if n <= gracia_total:
            pg = TipoGracia.TOTAL
        elif n <= gracia_total + gracia_parcial:
            pg = TipoGracia.PARCIAL
        else:
            pg = TipoGracia.SIN_GRACIA

        # --- Cuotón ---
        int_cut = saldo_cut * tem
        desg_cut = saldo_cut * pct_seg_desgravamen
        amort_cut = Decimal(0)
        saldo_cut_fin = saldo_cut + int_cut + desg_cut   # capitaliza todo

        fila_cut = FilaCuoton(
            saldo_ini=saldo_cut,
            interes=-int_cut,
            amort=-amort_cut,
            seg_desg=-desg_cut,
            saldo_fin=saldo_cut_fin,
        )

        # --- Regular ---
        int_reg = saldo_reg * tem
        desg_reg = saldo_reg * pct_seg_desgravamen

        if pg == TipoGracia.TOTAL:
            # No se paga cuota; interés se capitaliza
            cuota_pagada = Decimal(0)
            amort_reg = Decimal(0)
            saldo_reg_fin = saldo_reg + int_reg
        elif pg == TipoGracia.PARCIAL:
            # Solo interés
            cuota_pagada = int_reg + desg_reg
            amort_reg = Decimal(0)
            saldo_reg_fin = saldo_reg
        else:
            # Francés normal
            cuota_pagada = cuota_regular
            amort_reg = cuota_pagada - int_reg - desg_reg
            saldo_reg_fin = saldo_reg - amort_reg

        fila_reg = FilaRegular(
            saldo_ini=saldo_reg,
            interes=-int_reg,
            cuota=-cuota_pagada,
            amort=-amort_reg,
            seg_desg=-desg_reg,
            seg_riesgo=-seg_riesgo,
            gps=-gps,
            portes=-portes,
            gastos_adm=-gastos_adm,
            saldo_fin=saldo_reg_fin,
        )

        # --- Flujo del período (perspectiva deudor) ---
        if pg == TipoGracia.TOTAL:
            # Solo costos periódicos no-cuota
            flujo = -(desg_reg + seg_riesgo + gps + portes + gastos_adm)
        elif pg == TipoGracia.PARCIAL:
            flujo = -(cuota_pagada + seg_riesgo + gps + portes + gastos_adm)
        else:
            flujo = -(cuota_pagada + seg_riesgo + gps + portes + gastos_adm)

        filas.append(FilaCronograma(n=n, pg=pg, cuoton=fila_cut, regular=fila_reg, flujo=flujo))

        saldo_reg = saldo_reg_fin
        saldo_cut = saldo_cut_fin

    # Período final N+1: liquidación del cuotón
    int_cut_final = saldo_cut * tem
    desg_cut_final = saldo_cut * pct_seg_desgravamen
    amort_cut_final = saldo_cut + int_cut_final + desg_cut_final  # paga todo

    fila_cut_final = FilaCuoton(
        saldo_ini=saldo_cut,
        interes=-int_cut_final,
        amort=-amort_cut_final,
        seg_desg=-desg_cut_final,
        saldo_fin=Decimal(0),
    )
    fila_reg_final = FilaRegular(
        saldo_ini=Decimal(0),
        interes=Decimal(0),
        cuota=Decimal(0),
        amort=Decimal(0),
        seg_desg=Decimal(0),
        seg_riesgo=-seg_riesgo,
        gps=-gps,
        portes=-portes,
        gastos_adm=-gastos_adm,
        saldo_fin=Decimal(0),
    )
    flujo_final = -(amort_cut_final + seg_riesgo + gps + portes + gastos_adm)
    filas.append(
        FilaCronograma(
            n=num_cuotas + 1,
            pg=TipoGracia.SIN_GRACIA,
            cuoton=fila_cut_final,
            regular=fila_reg_final,
            flujo=flujo_final,
        )
    )

    return saldo_regular_0, cuota_regular, filas
