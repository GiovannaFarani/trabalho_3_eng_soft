"""Providers de segurança do evidence-service (mesma ideia do core-service).

Uso na rota do REQ 12 (Pessoa 3):

    from app.security.auth import AuthenticatedUser, get_current_user

    @router.get("/api/records")
    def list_records(user: AuthenticatedUser = Depends(get_current_user)):
        # isolamento de tenant (ADR-010): SEMPRE user.id, nunca userId da URL
        ... WHERE user_id = %s  (user.id)

No main.py:  app.dependency_overrides[auth.get_token_verifier] = get_token_verifier
             app.add_middleware(CorrelationIdMiddleware)
             configure_logging(settings.service_name)
"""
from functools import lru_cache

from fastapi import Depends

from app.config import Settings, get_settings
from app.db import Database
from app.security import auth
from app.security.token_blacklist import ITokenBlacklist, PostgresTokenBlacklist


@lru_cache
def get_database() -> Database:
    return Database(get_settings().database_url)


def get_token_blacklist(db: Database = Depends(get_database)) -> ITokenBlacklist:
    return PostgresTokenBlacklist(db)


def get_token_verifier(
    settings: Settings = Depends(get_settings),
    blacklist: ITokenBlacklist = Depends(get_token_blacklist),
) -> auth.TokenVerifier:
    return auth.TokenVerifier(settings.jwt_secret, settings.jwt_algorithm, blacklist)
