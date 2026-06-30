from sqlalchemy.orm import Session
from app.models.cliente import Cliente
from app.schemas.cliente import ClienteIn


def get_by_id(db: Session, cliente_id: int, usuario_id: int) -> Cliente | None:
    return db.query(Cliente).filter(
        Cliente.id == cliente_id, Cliente.usuario_id == usuario_id
    ).first()


def get_by_documento(db: Session, numero_documento: str, usuario_id: int) -> Cliente | None:
    return db.query(Cliente).filter(
        Cliente.numero_documento == numero_documento,
        Cliente.usuario_id == usuario_id,
    ).first()


def listar(db: Session, usuario_id: int) -> list[Cliente]:
    return db.query(Cliente).filter(Cliente.usuario_id == usuario_id).all()


def crear(db: Session, data: ClienteIn, usuario_id: int) -> Cliente:
    c = Cliente(**data.model_dump(), usuario_id=usuario_id)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c
