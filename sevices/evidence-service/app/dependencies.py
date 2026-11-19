
from functools import lru_cache

from fastapi import Depends

from app.config import Settings, get_settings
from app.db import Database
from app.security import auth
from app.security.token_blacklist import PostgresTokenBlacklist


@lru_cache
def get_database() -> Database:
    return Database(get_settings().database_url)


def get_token_blacklist(
    db: Database = Depends(get_database)
) -> PostgresTokenBlacklist:
    return PostgresTokenBlacklist(db)


def get_token_verifier(
    settings: Settings = Depends(get_settings),
    blacklist: PostgresTokenBlacklist = Depends(get_token_blacklist)
) -> auth.TokenVerifier:

    return auth.TokenVerifier(
        settings.jwt_secret,
        settings.jwt_algorithm,
        blacklist
    )
