"""Contratos HTTP (corpo das requisições) da recuperação de senha."""
from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1, max_length=200)
    # bcrypt só usa os primeiros 72 bytes: limitamos para evitar senhas truncadas.
    nova_senha: str = Field(min_length=1, max_length=72)


class MessageResponse(BaseModel):
    message: str
