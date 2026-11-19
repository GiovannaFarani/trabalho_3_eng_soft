"""Configuração do core-service, lida de variáveis de ambiente (.env).

Falha rápido (fail-fast): se algo obrigatório faltar, o serviço nem sobe,
em vez de falhar no meio de uma requisição.
"""
import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class ConfigError(RuntimeError):
    """Variável de ambiente obrigatória ausente ou inválida."""


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigError(f"Variável de ambiente obrigatória ausente: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    service_name: str
    database_url: str
    jwt_secret: str
    jwt_algorithm: str
    rabbitmq_url: str
    password_recovery_queue: str
    reset_token_ttl_minutes: int
    jwt_expires_minutes: int
    cors_origins: tuple


def load_settings() -> Settings:
    try:
        ttl = int(os.getenv("RESET_TOKEN_TTL_MINUTES", "15"))
    except ValueError as exc:
        raise ConfigError("RESET_TOKEN_TTL_MINUTES deve ser um inteiro") from exc
    try:
        jwt_ttl = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
    except ValueError as exc:
        raise ConfigError("JWT_EXPIRES_MINUTES deve ser um inteiro") from exc
    cors = tuple(
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if o.strip()
    )
    return Settings(
        service_name=os.getenv("SERVICE_NAME", "core-service"),
        database_url=_required("DATABASE_URL"),
        jwt_secret=_required("JWT_SECRET"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        rabbitmq_url=os.getenv("RABBITMQ_URL", "amqp://veridt:veridt_password@localhost:5672/"),
        password_recovery_queue=os.getenv(
            "PASSWORD_RECOVERY_QUEUE", "password_recovery_queue"
        ),
        reset_token_ttl_minutes=ttl,
        jwt_expires_minutes=jwt_ttl,
        cors_origins=cors,
    )


@lru_cache
def get_settings() -> Settings:
    return load_settings()
