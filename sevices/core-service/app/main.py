"""
INTEGRAÇÃO: este `main.py` é o mínimo para a Pessoa 2 rodar sozinha. A Pessoa 1
deve incluir aqui os routers de /api/auth/register, /login e /logout
(`app.include_router(auth_router)`). Os middlewares abaixo já valem para todos.

Execução: uvicorn app.main:create_app --factory --port 3001
ou:       uvicorn app.main:app --port 3001
"""

from fastapi import FastAPI

from app.config import get_settings
from app.dependencies import get_token_verifier
from app.logging_config import configure_logging
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.routers.password_recovery_router import router as password_recovery_router
from app.security import auth


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.service_name)

    app = FastAPI(title="Veridt - Core & Billing Service (IAM)", version="1.0.0")
    app.add_middleware(CorrelationIdMiddleware)  # ADR-009
    # Liga o validador concreto de JWT (assinatura + exp + blacklist no Postgres).
    app.dependency_overrides[auth.get_token_verifier] = get_token_verifier

    app.include_router(password_recovery_router)  # REQ 02 (Pessoa 2)
    # app.include_router(auth_router)             # REQ 01/03/04 (Pessoa 1)

    @app.get("/health", tags=["infra"])
    def health() -> dict:
        return {"status": "ok", "service": settings.service_name}

    return app


app = create_app()