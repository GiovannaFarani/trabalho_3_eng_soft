from fastapi import FastAPI 
from app.records.routes import router as records_router
from app.security import auth
from app.dependencies import get_token_verifier


app = FastAPI(
    title = "Evidence Service",
    description = "Serviço de Gerenciamento de Evidências e Notificações do Veridt",
    version = "1.0.0"
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
