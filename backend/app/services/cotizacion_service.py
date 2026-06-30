from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.domain.engine import simular
from app.repositories import cotizacion_repo
from app.schemas.cotizacion import SimulacionInput, CronogramaOut, CotizacionDetalleOut
from app.domain.enums import TipoTasa, Capitalizacion


def simular_sin_guardar(inp: SimulacionInput) -> CronogramaOut:
    resultado = simular(inp)
    return _to_cronograma_out(resultado)


def crear_cotizacion(db: Session, usuario_id: int, cliente_id: int, inp: SimulacionInput):
    resultado = simular(inp)
    cot = cotizacion_repo.guardar(db, usuario_id, cliente_id, inp, resultado.cabecera)
    return cot


def obtener_detalle(db: Session, cot_id: int, usuario_id: int) -> CotizacionDetalleOut:
    cot = cotizacion_repo.get_by_id(db, cot_id, usuario_id)
    if not cot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cotización no encontrada")

    inp = SimulacionInput(
        moneda=cot.moneda,
        precio_venta=float(cot.precio_venta),
        pct_cuota_inicial=float(cot.pct_cuota_inicial),
        pct_cuota_final=float(cot.pct_cuota_final),
        num_anios=cot.num_anios,
        num_cuotas=cot.num_cuotas,
        tasa_valor=float(cot.tasa_valor),
        tasa_tipo=TipoTasa(cot.tasa_tipo),
        capitalizacion=Capitalizacion(cot.capitalizacion) if cot.capitalizacion else None,
        frecuencia_dias=cot.frecuencia_dias,
        dias_anio=cot.dias_anio,
        cok_anual=float(cot.cok_anual) if cot.cok_anual else 0.50,
        costes_iniciales=cot.costes_iniciales or {},
        costes_periodicos=cot.costes_periodicos or {},
        gracia=cot.gracia or {"total": 0, "parcial": 0},
        veh_marca=cot.veh_marca,
        veh_modelo=cot.veh_modelo,
        veh_anio=cot.veh_anio,
    )
    resultado = simular(inp)
    return CotizacionDetalleOut(
        id=cot.id,
        cliente_id=cot.cliente_id,
        cronograma_completo=_to_cronograma_out(resultado),
    )


def _to_cronograma_out(resultado) -> CronogramaOut:
    from app.schemas.cotizacion import (
        CabeceraOut, FilaCronogramaOut, FilaCuotonOut, FilaRegularOut
    )

    cab = resultado.cabecera
    cabecera_out = CabeceraOut(
        tea=float(cab.tea),
        tem=float(cab.tem),
        cuota_inicial=float(cab.cuota_inicial),
        cuota_final=float(cab.cuota_final),
        monto_prestamo=float(cab.monto_prestamo),
        saldo_regular=float(cab.saldo_regular),
        cuota_regular=float(cab.cuota_regular),
        tir_mensual=float(cab.tir_mensual),
        tcea=float(cab.tcea),
        van=float(cab.van),
    )

    filas_out = []
    for f in resultado.cronograma:
        filas_out.append(FilaCronogramaOut(
            n=f.n,
            pg=f.pg.value,
            cuoton=FilaCuotonOut(
                saldo_ini=float(f.cuoton.saldo_ini),
                interes=float(f.cuoton.interes),
                amort=float(f.cuoton.amort),
                seg_desg=float(f.cuoton.seg_desg),
                saldo_fin=float(f.cuoton.saldo_fin),
            ),
            regular=FilaRegularOut(
                saldo_ini=float(f.regular.saldo_ini),
                interes=float(f.regular.interes),
                cuota=float(f.regular.cuota),
                amort=float(f.regular.amort),
                seg_desg=float(f.regular.seg_desg),
                seg_riesgo=float(f.regular.seg_riesgo),
                gps=float(f.regular.gps),
                portes=float(f.regular.portes),
                gastos_adm=float(f.regular.gastos_adm),
                saldo_fin=float(f.regular.saldo_fin),
            ),
            flujo=float(f.flujo),
        ))

    return CronogramaOut(cabecera=cabecera_out, cronograma=filas_out)
