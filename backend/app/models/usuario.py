from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    clientes = relationship("Cliente", back_populates="usuario")
    cotizaciones = relationship("Cotizacion", back_populates="usuario")
