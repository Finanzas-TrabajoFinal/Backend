from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    nombres = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    tipo_documento = Column(String, default="DNI")
    numero_documento = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="clientes")
    cotizaciones = relationship("Cotizacion", back_populates="cliente")
