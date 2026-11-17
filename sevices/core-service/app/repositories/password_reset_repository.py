"""Repository da tabela `password_resets` (SRP: só SQL, nenhuma regra de negócio).

Os métodos recebem o cursor da transação aberta pelo service, assim várias
operações (ex.: consumir token + trocar senha) ficam na MESMA transação ACID.

O que vai para a coluna `reset_token` é o HASH SHA-256 do token (64 chars hex,
cabe em VARCHAR(100)). O token em texto puro só existe no e-mail. Se alguém
ler o banco, não consegue redefinir senhas.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class IPasswordResetRepository(ABC):
    @abstractmethod
    def invalidate_pending(self, cur, user_id: str) -> None: ...

    @abstractmethod
    def create(self, cur, user_id: str, token_hash: str, expires_at: datetime) -> None: ...

    @abstractmethod
    def consume_valid(self, cur, token_hash: str, now: datetime) -> Optional[str]:
        """Marca o token como usado e devolve o user_id, se ele for válido
        (existe, não usado e não expirado). Caso contrário, devolve None."""


class PgPasswordResetRepository(IPasswordResetRepository):
    def invalidate_pending(self, cur, user_id: str) -> None:
        cur.execute(
            "UPDATE password_resets SET used = TRUE "
            "WHERE user_id = %s AND COALESCE(used, FALSE) = FALSE",
            (user_id,),
        )

    def create(self, cur, user_id: str, token_hash: str, expires_at: datetime) -> None:
        cur.execute(
            "INSERT INTO password_resets (user_id, reset_token, expires_at) VALUES (%s, %s, %s)",
            (user_id, token_hash, expires_at),
        )

    def consume_valid(self, cur, token_hash: str, now: datetime) -> Optional[str]:
        # UPDATE ... RETURNING é atômico: dois pedidos simultâneos com o mesmo
        # token não conseguem ambos "consumi-lo".
        cur.execute(
            "UPDATE password_resets SET used = TRUE "
            "WHERE reset_token = %s AND COALESCE(used, FALSE) = FALSE AND expires_at > %s "
            "RETURNING user_id",
            (token_hash, now),
        )
        row = cur.fetchone()
        return str(row["user_id"]) if row else None
