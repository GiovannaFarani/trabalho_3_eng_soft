import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.records.routes import router as records_router
from app.security import auth
from app.dependencies import get_token_verifier

DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"


def _parse_cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
    return [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]


app = FastAPI(
    title = "Evidence Service",
    description = "Serviço de Gerenciamento de Evidências e Notificações do Veridt",
    version = "1.0.0"
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
