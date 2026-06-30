from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas.cotizacion import (
    SimulacionInput, CronogramaOut, CotizacionCreateIn,
    CotizacionResumenOut, CotizacionDetalleOut,
)
from app.services import cotizacion_service
from app.repositories import cotizacion_repo

router = APIRouter(tags=["cotizaciones"])


@router.post("/simular", response_model=CronogramaOut)
def simular(
    inp: SimulacionInput,
    usuario: Usuario = Depends(get_current_user),
):
    """Calcula el cronograma completo sin persistir nada."""
    return cotizacion_service.simular_sin_guardar(inp)


@router.post("/cotizaciones", response_model=CotizacionResumenOut, status_code=201)
def crear_cotizacion(
    data: CotizacionCreateIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    cot = cotizacion_service.crear_cotizacion(db, usuario.id, data.cliente_id, data.simulacion)
    return cot


@router.get("/cotizaciones", response_model=list[CotizacionResumenOut])
def listar_cotizaciones(
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return cotizacion_repo.listar(db, usuario.id)


@router.get("/cotizaciones/{cot_id}", response_model=CotizacionDetalleOut)
def detalle_cotizacion(
    cot_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return cotizacion_service.obtener_detalle(db, cot_id, usuario.id)
