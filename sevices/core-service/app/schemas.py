"""Contratos HTTP (corpo das requisições e respostas) do core-service."""
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1, max_length=200)
    # bcrypt só usa os primeiros 72 bytes: limitamos para evitar senhas truncadas.
    nova_senha: str = Field(min_length=1, max_length=72)


class MessageResponse(BaseModel):
    message: str


# ------------------------------------------------- Cadastro / Login / Logout
# Campos do Apêndice A / Tela 1 (REQ 01, Decisão D1) e do REQ 03.
class RegisterRequest(BaseModel):
    nome_completo: str = Field(min_length=3, max_length=150)
    email: EmailStr = Field(max_length=150)
    senha: str = Field(min_length=1, max_length=72)
    cpf: str = Field(min_length=11, max_length=14)
    tipo_perfil: Literal["ADVOGADO", "USUARIO_COMUM"]
    numero_oab: Optional[str] = Field(default=None, max_length=30)
    # Sem default True: o aceite precisa vir explícito do usuário (LGPD).
    termos_aceitos: bool = False


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=200)


class UserResponse(BaseModel):
    id: str
    nome_completo: str
    email: str
    cpf: str
    tipo_perfil: str
    numero_oab: Optional[str]


class LoginResponse(BaseModel):
    token: str
    token_type: str = "Bearer"
    user: UserResponse
