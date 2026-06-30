from pydantic import BaseModel
from datetime import datetime


class ClienteIn(BaseModel):
    nombres: str
    apellidos: str
    tipo_documento: str = "DNI"
    numero_documento: str


class ClienteOut(BaseModel):
    id: int
    nombres: str
    apellidos: str
    tipo_documento: str
    numero_documento: str
    created_at: datetime

    model_config = {"from_attributes": True}
