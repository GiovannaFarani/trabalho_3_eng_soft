"""Política de senha forte (Tela 1 / REQ 01 / REQ 02).

INTEGRAÇÃO: a mesma regra é usada pela Pessoa 1 no cadastro. Está aqui em um
único lugar para a Pessoa 1 poder IMPORTAR esta função (e não duplicar a regex).
Regra do roteiro: >= 8 caracteres, com letras, números e símbolos.
"""
import re

_STRONG_PASSWORD = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$")

PASSWORD_RULE_MESSAGE = (
    "A senha deve ter no mínimo 8 caracteres, com letras, números e símbolos (@$!%*#?&)."
)


def is_strong_password(password: str) -> bool:
    return bool(_STRONG_PASSWORD.match(password or ""))
