"""Acesso ao PostgreSQL (pool de conexões + transação).

INTEGRAÇÃO: o pool de conexão é responsabilidade da Pessoa 1. Este arquivo é a
versão mínima necessária para a Pessoa 2 funcionar sozinha; se a Pessoa 1 já
tiver um módulo de conexão, basta manter a interface `transaction()` (context
manager que entrega um cursor e faz commit/rollback).
"""
from contextlib import contextmanager

from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool


class Database:
    def __init__(self, dsn: str, minconn: int = 1, maxconn: int = 10) -> None:
        self._pool = ThreadedConnectionPool(minconn, maxconn, dsn)

    @contextmanager
    def transaction(self):
        """Entrega um cursor; commit ao sair com sucesso, rollback em exceção."""
        conn = self._pool.getconn()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                yield cur
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._pool.putconn(conn)

    def close(self) -> None:
        self._pool.closeall()
