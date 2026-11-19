"""
Core & Billing Service (IAM) - porta 3001.
  - REQ 01/03/04 (Pessoa 1): /api/auth/register, /login, /logout
  - REQ 02       (Pessoa 2): /api/auth/forgot-password, /reset-password

Execução: uvicorn app.main:create_app --factory --port 3001
ou:       uvicorn app.main:app --port 3001
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.dependencies import get_token_verifier
from app.logging_config import configure_logging
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.routers.auth_router import router as auth_router
from app.routers.password_recovery_router import router as password_recovery_router
from app.security import auth


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.service_name)

    app = FastAPI(title="Veridt - Core & Billing Service (IAM)", version="1.0.0")
    app.add_middleware(CorrelationIdMiddleware)  # ADR-009
    # Portal Web (porta 5173) chama este serviço direto do navegador.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Correlation-ID"],
        expose_headers=["X-Correlation-ID"],
    )
    # Liga o validador concreto de JWT (assinatura + exp + blacklist no Postgres).
    app.dependency_overrides[auth.get_token_verifier] = get_token_verifier

    app.include_router(password_recovery_router)  # REQ 02 (Pessoa 2)
    app.include_router(auth_router)               # REQ 01/03/04 (Pessoa 1)

    @app.get("/health", tags=["infra"])
    def health() -> dict:
        return {"status": "ok", "service": settings.service_name}

    return app


app = create_app()