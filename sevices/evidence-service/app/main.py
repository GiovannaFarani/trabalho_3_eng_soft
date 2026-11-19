from contextlib import asynccontextmanager
import logging
import os
import threading

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.dependencies import get_token_verifier
from app.notifications.email_sender import EmailSender
from app.notifications.password_recovery_handler import PasswordRecoveryHandler
from app.notifications.rabbitmq_consumer import RabbitMQConsumer
from app.records.routes import router as records_router
from app.security import auth

logger = logging.getLogger(__name__)

DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


def _parse_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
    return [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]


def _is_embedded_consumer_enabled() -> bool:
    return os.getenv("ENABLE_EMBEDDED_CONSUMER", "false").strip().lower() in {
        "1",
        "true",
        "yes",
    }


def _run_consumer_loop(stop_event: threading.Event) -> None:
    try:
        settings = get_settings()
    except Exception:
        logger.exception("Falha ao carregar configurações do consumidor SMTP/RabbitMQ.")
        return

    email_sender = EmailSender(
        host=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        sender=settings.smtp_from,
    )
    handler = PasswordRecoveryHandler(
        email_sender=email_sender,
        frontend_reset_url=settings.frontend_reset_url,
    )
    consumer = RabbitMQConsumer(
        rabbitmq_url=settings.rabbitmq_url,
        handler=handler,
    )

    while not stop_event.is_set():
        try:
            logger.info("Iniciando consumidor embutido de recuperação de senha (RabbitMQ + SMTP).")
            consumer.start()
        except Exception:
            logger.exception("Consumidor RabbitMQ interrompido; tentando reconectar em 5s.")
            stop_event.wait(5)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    stop_event = threading.Event()
    if _is_embedded_consumer_enabled():
        thread = threading.Thread(
            target=_run_consumer_loop,
            args=(stop_event,),
            name="password-recovery-consumer",
            daemon=True,
        )
        thread.start()
    try:
        yield
    finally:
        stop_event.set()


app = FastAPI(
    title = "Evidence Service",
    description = "Serviço de Gerenciamento de Evidências e Notificações do Veridt",
    version = "1.0.0",
    lifespan = lifespan,
)

cors_origins = _parse_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials="*" not in cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)

# Configura o provider de validação JWT
app.dependency_overrides[auth.get_token_verifier] = get_token_verifier

app.include_router(records_router)


@app.get("/")
def inicio():
    return {
        "mensagem": "Evidence Service funcionando!"
    }


@app.get("/health")
def verificar_saude():
    return {
        "status": "Online"
    }
