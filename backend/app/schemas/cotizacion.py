from __future__ import annotations
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from app.domain.enums import TipoTasa, Capitalizacion, Moneda


class SimulacionInput(BaseModel):
    moneda: Moneda = Moneda.PEN
    precio_venta: float = Field(..., gt=0, description="Precio de venta del vehículo")
    pct_cuota_inicial: float = Field(..., ge=0, le=1, description="Porcentaje de cuota inicial (ej. 0.20)")
    pct_cuota_final: float = Field(..., ge=0, le=1, description="Porcentaje de cuota final/balón (ej. 0.40)")
    num_anios: int = Field(..., gt=0, description="Plazo en años")
    num_cuotas: int = Field(..., gt=0, description="Total de cuotas mensuales")
    tasa_valor: float = Field(..., gt=0, description="Valor de la tasa (TNA o TEA)")
    tasa_tipo: TipoTasa = Field(..., description="Tipo de tasa: TNA o TEA")
    capitalizacion: Optional[Capitalizacion] = Field(None, description="Requerido si tasa_tipo=TNA")
    frecuencia_dias: int = Field(30, description="Duración de cada período en días")
    dias_anio: int = Field(360, description="Días por año (360 o 365)")
    costes_iniciales: dict[str, float] = Field(
        default_factory=dict,
        description="Costos iniciales financiados: {notariales, registrales, ...}"
    )
    costes_periodicos: dict[str, float] = Field(
        default_factory=dict,
        description="Costos periódicos: {gps, portes, gastos_adm, pct_seg_desgravamen, pct_seg_riesgo}"
    )
    gracia: dict[str, int] = Field(
        default_factory=lambda: {"total": 0, "parcial": 0},
        description="Períodos de gracia: {total: N, parcial: M}"
    )
    cok_anual: float = Field(0.50, description="Costo de oportunidad anual del deudor")

    # Datos del vehículo (opcionales para simulación, requeridos para guardar)
    veh_marca: Optional[str] = None
    veh_modelo: Optional[str] = None
    veh_anio: Optional[int] = None


# --- Objetos de respuesta del cronograma ---

class FilaCuotonOut(BaseModel):
    saldo_ini: float
    interes: float
    amort: float
    seg_desg: float
    saldo_fin: float


class FilaRegularOut(BaseModel):
    saldo_ini: float
    interes: float
    cuota: float
    amort: float
    seg_desg: float
    seg_riesgo: float
    gps: float
    portes: float
    gastos_adm: float
    saldo_fin: float


class FilaCronogramaOut(BaseModel):
    n: int
    pg: str
    cuoton: FilaCuotonOut
    regular: FilaRegularOut
    flujo: float


class CabeceraOut(BaseModel):
    tea: float
    tem: float
    cuota_inicial: float
    cuota_final: float
    monto_prestamo: float
    saldo_regular: float
    cuota_regular: float
    tir_mensual: float
    tcea: float
    van: float


class CronogramaOut(BaseModel):
    cabecera: CabeceraOut
    cronograma: list[FilaCronogramaOut]


# --- Cotización persistida ---

class CotizacionCreateIn(BaseModel):
    cliente_id: int
    simulacion: SimulacionInput


class CotizacionResumenOut(BaseModel):
    id: int
    cliente_id: int
    veh_marca: Optional[str]
    veh_modelo: Optional[str]
    veh_anio: Optional[int]
    moneda: str
    precio_venta: float
    num_cuotas: int
    tea: Optional[float]
    cuota_regular: Optional[float]
    tcea: Optional[float]
    van: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class CotizacionDetalleOut(BaseModel):
    id: int
    cliente_id: int
    cronograma_completo: CronogramaOut
