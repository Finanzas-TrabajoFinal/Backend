from pydantic import BaseModel, EmailStr


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    nombre: str


class UsuarioOut(BaseModel):
    id: int
    email: str
    nombre: str

    model_config = {"from_attributes": True}
