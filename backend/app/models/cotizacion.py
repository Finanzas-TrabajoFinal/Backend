from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Cotizacion(Base):
    __tablename__ = "cotizaciones"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    # Vehículo (embebido)
    veh_marca = Column(String)
    veh_modelo = Column(String)
    veh_anio = Column(Integer)

    # Inputs financieros principales
    moneda = Column(String(3), nullable=False, default="PEN")
    precio_venta = Column(Numeric(14, 2), nullable=False)
    pct_cuota_inicial = Column(Numeric(6, 4), nullable=False)
    pct_cuota_final = Column(Numeric(6, 4), nullable=False)
    num_anios = Column(Integer, nullable=False)
    num_cuotas = Column(Integer, nullable=False)
    tasa_valor = Column(Numeric(8, 6), nullable=False)
    tasa_tipo = Column(String(3), nullable=False)
    capitalizacion = Column(String(10))
    frecuencia_dias = Column(Integer, default=30)
    dias_anio = Column(Integer, default=360)
    cok_anual = Column(Numeric(8, 6))

    # Inputs secundarios en JSONB
    costes_iniciales = Column(JSONB)
    costes_periodicos = Column(JSONB)
    gracia = Column(JSONB)

    # Indicadores de cabecera (caché)
    tea = Column(Numeric(10, 8))
    tem = Column(Numeric(10, 8))
    cuota_inicial = Column(Numeric(14, 2))
    cuota_final = Column(Numeric(14, 2))
    monto_prestamo = Column(Numeric(14, 2))
    saldo_regular = Column(Numeric(14, 4))
    cuota_regular = Column(Numeric(14, 4))
    tir_mensual = Column(Numeric(10, 8))
    tcea = Column(Numeric(10, 8))
    van = Column(Numeric(14, 2))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="cotizaciones")
    cliente = relationship("Cliente", back_populates="cotizaciones")
