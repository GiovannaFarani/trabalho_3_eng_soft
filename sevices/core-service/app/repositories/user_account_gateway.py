"""Porta (interface) de acesso a usuários para a recuperação de senha.

INTEGRAÇÃO COM A PESSOA 1: o service só precisa de duas operações sobre
`users`. A implementação abaixo é um ADAPTADOR MÍNIMO de integração: se a
Pessoa 1 já tiver um UserRepository com essas operações, basta trocar o adapter
em app/dependencies.py, sem tocar no service.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserAccount:
    id: str
    nome_completo: str
    email: str


class IUserAccountGateway(ABC):
    @abstractmethod
    def find_by_email(self, cur, email: str) -> Optional[UserAccount]: ...

    @abstractmethod
    def update_password_hash(self, cur, user_id: str, password_hash: str) -> None: ...


class PgUserAccountGateway(IUserAccountGateway):
    """[ADAPTADOR DE INTEGRAÇÃO - tabela `users` pertence à Pessoa 1]"""

    def find_by_email(self, cur, email: str) -> Optional[UserAccount]:
        cur.execute(
            "SELECT id, nome_completo, email FROM users WHERE LOWER(email) = LOWER(%s)",
            (email,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return UserAccount(
            id=str(row["id"]), nome_completo=row["nome_completo"], email=row["email"]
        )

    def update_password_hash(self, cur, user_id: str, password_hash: str) -> None:
        cur.execute("UPDATE users SET senha_hash = %s WHERE id = %s", (password_hash, user_id))
