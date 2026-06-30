from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.core.security import hash_password


def get_by_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()


def get_by_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def crear(db: Session, email: str, password: str, nombre: str) -> Usuario:
    u = Usuario(email=email, hashed_password=hash_password(password), nombre=nombre)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u
