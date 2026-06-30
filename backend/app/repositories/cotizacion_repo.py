from sqlalchemy.orm import Session
from app.models.cotizacion import Cotizacion
from app.schemas.cotizacion import SimulacionInput
from app.domain.engine import CabeceraCronograma


def guardar(
    db: Session,
    usuario_id: int,
    cliente_id: int,
    inp: SimulacionInput,
    cab: CabeceraCronograma,
) -> Cotizacion:
    cot = Cotizacion(
        usuario_id=usuario_id,
        cliente_id=cliente_id,
        veh_marca=inp.veh_marca,
        veh_modelo=inp.veh_modelo,
        veh_anio=inp.veh_anio,
        moneda=inp.moneda,
        precio_venta=inp.precio_venta,
        pct_cuota_inicial=inp.pct_cuota_inicial,
        pct_cuota_final=inp.pct_cuota_final,
        num_anios=inp.num_anios,
        num_cuotas=inp.num_cuotas,
        tasa_valor=inp.tasa_valor,
        tasa_tipo=inp.tasa_tipo,
        capitalizacion=inp.capitalizacion,
        frecuencia_dias=inp.frecuencia_dias,
        dias_anio=inp.dias_anio,
        cok_anual=inp.cok_anual,
        costes_iniciales=inp.costes_iniciales,
        costes_periodicos=inp.costes_periodicos,
        gracia=inp.gracia,
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
    db.add(cot)
    db.commit()
    db.refresh(cot)
    return cot


def listar(db: Session, usuario_id: int) -> list[Cotizacion]:
    return (
        db.query(Cotizacion)
        .filter(Cotizacion.usuario_id == usuario_id)
        .order_by(Cotizacion.created_at.desc())
        .all()
    )


def get_by_id(db: Session, cot_id: int, usuario_id: int) -> Cotizacion | None:
    return db.query(Cotizacion).filter(
        Cotizacion.id == cot_id, Cotizacion.usuario_id == usuario_id
    ).first()
