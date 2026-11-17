"""Blacklist de tokens revogados (ADR-005, logout do REQ 04).

A Pessoa 1 INSERE tokens em `revoked_tokens` no logout; aqui só CONSULTAMOS.
A abstração ITokenBlacklist permite testar a autenticação sem banco (DIP).
"""
from abc import ABC, abstractmethod

from app.db import Database


class ITokenBlacklist(ABC):
    @abstractmethod
    def is_revoked(self, token: str) -> bool:
        """True se o token foi revogado (logout)."""


class PostgresTokenBlacklist(ITokenBlacklist):
    def __init__(self, database: Database) -> None:
        self._db = database

    def is_revoked(self, token: str) -> bool:
        with self._db.transaction() as cur:
            cur.execute("SELECT 1 FROM revoked_tokens WHERE token = %s", (token,))
            return cur.fetchone() is not None
