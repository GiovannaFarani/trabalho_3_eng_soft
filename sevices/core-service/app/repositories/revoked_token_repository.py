"""Escrita na blacklist de tokens (REQ 04 - Logout, ADR-005).

A LEITURA da blacklist (`is_revoked`) fica em app/security/token_blacklist.py,
que é copiado para o evidence-service. A ESCRITA só acontece no logout, que é
exclusivo do core-service, por isso fica aqui (ISP: quem só consulta não
precisa conhecer o método de revogar, e vice-versa).
"""
from abc import ABC, abstractmethod
from datetime import datetime


class IRevokedTokenRepository(ABC):
    @abstractmethod
    def revoke(self, cur, token: str, expires_at: datetime) -> None:
        """Coloca o token na blacklist até `expires_at` (idempotente)."""


class PgRevokedTokenRepository(IRevokedTokenRepository):
    def revoke(self, cur, token: str, expires_at: datetime) -> None:
        cur.execute(
            "INSERT INTO revoked_tokens (token, expires_at) VALUES (%s, %s) "
            "ON CONFLICT (token) DO NOTHING",
            (token, expires_at),
        )
