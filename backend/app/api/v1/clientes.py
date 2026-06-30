from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas.cliente import ClienteIn, ClienteOut
from app.repositories import cliente_repo

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.post("", response_model=ClienteOut, status_code=201)
def crear_cliente(
    data: ClienteIn,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    return cliente_repo.crear(db, data, usuario.id)


@router.get("", response_model=list[ClienteOut])
def listar_clientes(
    dni: str | None = Query(None, description="Buscar por número de documento"),
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    if dni:
        c = cliente_repo.get_by_documento(db, dni, usuario.id)
        return [c] if c else []
    return cliente_repo.listar(db, usuario.id)


@router.get("/{cliente_id}", response_model=ClienteOut)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    usuario: Usuario = Depends(get_current_user),
):
    c = cliente_repo.get_by_id(db, cliente_id, usuario.id)
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return c
