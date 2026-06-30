from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import LoginIn, TokenOut, UsuarioOut
from app.schemas.auth import LoginIn
from app.services import auth_service
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    nombre: str


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    return auth_service.login(db, data.email, data.password)


@router.post("/register", response_model=UsuarioOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    """Alta de asesores (uso interno / usuario semilla)."""
    return auth_service.registrar_asesor(db, data.email, data.password, data.nombre)
