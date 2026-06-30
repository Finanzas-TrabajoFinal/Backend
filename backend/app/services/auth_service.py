from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import usuario_repo
from app.core.security import verify_password, create_access_token


def login(db: Session, email: str, password: str) -> dict:
    usuario = usuario_repo.get_by_email(db, email)
    if not usuario or not verify_password(password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    token = create_access_token({"sub": str(usuario.id)})
    return {"access_token": token, "token_type": "bearer", "nombre": usuario.nombre}


def registrar_asesor(db: Session, email: str, password: str, nombre: str):
    if usuario_repo.get_by_email(db, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        )
    return usuario_repo.crear(db, email, password, nombre)
