"""UserRepository (REQ 01 / REQ 03) - camada de DADOS do SRP da Pessoa 1.

Responsabilidade ÚNICA: executar SQL na tabela `users`. Não valida senha,
não conhece JWT, não conhece HTTP. Quem decide as regras é o AuthService.

Os métodos recebem o cursor da transação aberta pelo service (mesmo padrão do
PasswordResetRepository da Pessoa 2), assim o service controla o commit.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from psycopg2 import errors as pg_errors

from app.domain.errors import CpfAlreadyRegisteredError, EmailAlreadyRegisteredError


@dataclass(frozen=True)
class NewUser:
    """Dados já validados pelo AuthService, prontos para persistir."""

    nome_completo: str
    email: str
    senha_hash: str
    cpf: str
    tipo_perfil: str
    numero_oab: Optional[str]
    termos_aceitos: bool


@dataclass(frozen=True)
class User:
    id: str
    nome_completo: str
    email: str
    senha_hash: str
    cpf: str
    tipo_perfil: str
    numero_oab: Optional[str]


class IUserRepository(ABC):
    @abstractmethod
    def find_by_email(self, cur, email: str) -> Optional[User]: ...

    @abstractmethod
    def find_by_cpf(self, cur, cpf: str) -> Optional[User]: ...

    @abstractmethod
    def create(self, cur, user: NewUser) -> User:
        """Insere o usuário. Levanta EmailAlreadyRegisteredError ou CpfAlreadyRegisteredError se já existirem."""


_COLUMNS = "id, nome_completo, email, senha_hash, cpf, tipo_perfil, numero_oab"


def _to_user(row) -> User:
    return User(
        id=str(row["id"]),
        nome_completo=row["nome_completo"],
        email=row["email"],
        senha_hash=row["senha_hash"],
        cpf=row["cpf"],
        tipo_perfil=row["tipo_perfil"],
        numero_oab=row["numero_oab"],
    )


class PgUserRepository(IUserRepository):
    def find_by_email(self, cur, email: str) -> Optional[User]:
        cur.execute(
            f"SELECT {_COLUMNS} FROM users WHERE LOWER(email) = LOWER(%s)", (email,)
        )
        row = cur.fetchone()
        return _to_user(row) if row else None

    def find_by_cpf(self, cur, cpf: str) -> Optional[User]:
        cur.execute(
            f"SELECT {_COLUMNS} FROM users WHERE cpf = %s", (cpf,)
        )
        row = cur.fetchone()
        return _to_user(row) if row else None

    def create(self, cur, user: NewUser) -> User:
        # A checagem prévia dá a resposta 409 no caso comum (inclusive para
        # e-mails que só diferem em maiúsculas/minúsculas, que a UNIQUE do
        # banco não pega). A UniqueViolation cobre a corrida entre dois
        # cadastros simultâneos com o mesmo e-mail ou CPF.
        if self.find_by_email(cur, user.email) is not None:
            raise EmailAlreadyRegisteredError("E-mail já cadastrado.")
        if self.find_by_cpf(cur, user.cpf) is not None:
            raise CpfAlreadyRegisteredError("CPF já cadastrado.")
        cur.execute("SAVEPOINT create_user")
        try:
            cur.execute(
                "INSERT INTO users (nome_completo, email, senha_hash, cpf, tipo_perfil, "
                "numero_oab, termos_aceitos) VALUES (%s, %s, %s, %s, %s, %s, %s) "
                f"RETURNING {_COLUMNS}",
                (
                    user.nome_completo,
                    user.email,
                    user.senha_hash,
                    user.cpf,
                    user.tipo_perfil,
                    user.numero_oab,
                    user.termos_aceitos,
                ),
            )
        except pg_errors.UniqueViolation as exc:
            cur.execute("ROLLBACK TO SAVEPOINT create_user")
            constraint = getattr(getattr(exc, "diag", None), "constraint_name", "") or ""
            if "cpf" in constraint.lower():
                raise CpfAlreadyRegisteredError("CPF já cadastrado.") from exc
            raise EmailAlreadyRegisteredError("E-mail já cadastrado.") from exc
        return _to_user(cur.fetchone())
