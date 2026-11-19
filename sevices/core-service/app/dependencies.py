"""Composition root: é AQUI (e só aqui) que implementações concretas são ligadas
às abstrações (injeção de dependência)."""
from functools import lru_cache

from fastapi import Depends

from app.config import Settings, get_settings
from app.db import Database
from app.messaging.publisher import IMessagePublisher
from app.messaging.rabbitmq_publisher import RabbitMqPublisher
from app.repositories.password_reset_repository import PgPasswordResetRepository
from app.repositories.revoked_token_repository import PgRevokedTokenRepository
from app.repositories.user_account_gateway import PgUserAccountGateway
from app.repositories.user_repository import PgUserRepository
from app.security import auth
from app.security.jwt_issuer import JwtTokenIssuer
from app.security.password_hasher import BcryptPasswordHasher, IPasswordHasher
from app.security.token_blacklist import ITokenBlacklist, PostgresTokenBlacklist
from app.services.auth_service import AuthService
from app.services.password_recovery_service import PasswordRecoveryService


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


def get_message_publisher(settings: Settings = Depends(get_settings)) -> IMessagePublisher:
    return RabbitMqPublisher(settings.rabbitmq_url)


def get_password_hasher() -> IPasswordHasher:
    return BcryptPasswordHasher()


def _bcrypt_hash(password: str) -> str:
    return get_password_hasher().hash(password)


def get_password_recovery_service(
    settings: Settings = Depends(get_settings),
    db: Database = Depends(get_database),
    publisher: IMessagePublisher = Depends(get_message_publisher),
) -> PasswordRecoveryService:
    return PasswordRecoveryService(
        users=PgUserAccountGateway(),
        resets=PgPasswordResetRepository(),
        publisher=publisher,
        transaction=db.transaction,
        hash_password=_bcrypt_hash,
        queue_name=settings.password_recovery_queue,
        token_ttl_minutes=settings.reset_token_ttl_minutes,
    )


def get_auth_service(
    settings: Settings = Depends(get_settings),
    db: Database = Depends(get_database),
    hasher: IPasswordHasher = Depends(get_password_hasher),
) -> AuthService:
    return AuthService(
        users=PgUserRepository(),
        revoked_tokens=PgRevokedTokenRepository(),
        hasher=hasher,
        tokens=JwtTokenIssuer(
            settings.jwt_secret, settings.jwt_algorithm, settings.jwt_expires_minutes
        ),
        transaction=db.transaction,
    )
