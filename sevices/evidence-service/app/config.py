
import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class ConfigError(RuntimeError):
    """Variável de ambiente obrigatória ausente."""


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ConfigError(
            f"Variável de ambiente obrigatória ausente: {name}"
        )
    return value


@dataclass(frozen=True)
class Settings:
    service_name: str
    database_url: str
    jwt_secret: str
    jwt_algorithm: str
    rabbitmq_url: str
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    smtp_from: str
    frontend_reset_url: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        service_name=os.getenv(
            "SERVICE_NAME", "evidence-service"
        ),
        database_url=_required("DATABASE_URL"),
        jwt_secret=_required("JWT_SECRET"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        rabbitmq_url=os.getenv(
            "RABBITMQ_URL",
            "amqp://veridt:veridt_password@localhost:5672/"
        ),
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_user=_required("SMTP_USER"),
        smtp_password=_required("SMTP_PASSWORD"),
        smtp_from=_required("SMTP_FROM"),
        frontend_reset_url=os.getenv(
            "FRONTEND_RESET_URL",
            "http://localhost:5173/reset-password"
        ),
    )

