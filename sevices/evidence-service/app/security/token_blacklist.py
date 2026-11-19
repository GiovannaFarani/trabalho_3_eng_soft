from abc import ABC, abstractmethod

from app.db import Database


class ITokenBlacklist(ABC):

    @abstractmethod
    def is_revoked(self, token: str) -> bool:
        """Verifica se o token foi revogado."""


class PostgresTokenBlacklist(ITokenBlacklist):

    def __init__(self, database: Database) -> None:
        self._db = database

    def is_revoked(self, token: str) -> bool:
        with self._db.transaction() as cur:
            cur.execute(
                "SELECT 1 FROM revoked_tokens WHERE token = %s",
                (token,)
            )

            return cur.fetchone() is not None
