
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.security.auth import AuthenticatedUser, get_current_user


@pytest.fixture
def client():
    # Preserva as configurações originais da aplicação
    overrides_originais = app.dependency_overrides.copy()

    with TestClient(app) as test_client:
        yield test_client

    # Restaura as dependências após cada teste
    app.dependency_overrides.clear()
    app.dependency_overrides.update(overrides_originais)


def simular_usuario(user_id):
    return AuthenticatedUser(
        id=user_id,
        nome="Usuario de Teste",
        email="teste@email.com",
        role="ADVOGADO",
        oab=None
    )


def test_listar_records_sem_autenticacao(client):
    resposta = client.get("/api/records/")

    assert resposta.status_code == 401


def test_listar_records_usuario_cadastrado(client):
    usuario_id = "11111111-1111-1111-1111-111111111111"

    app.dependency_overrides[get_current_user] = (
        lambda: simular_usuario(usuario_id)
    )

    resposta = client.get("/api/records/")

    assert resposta.status_code == 200
    assert len(resposta.json()) == 5


def test_listar_records_usuario_sem_registros(client):
    usuario_id = "22222222-2222-2222-2222-222222222222"

    app.dependency_overrides[get_current_user] = (
        lambda: simular_usuario(usuario_id)
    )

    resposta = client.get("/api/records/")

    assert resposta.status_code == 200
    assert resposta.json() == []
