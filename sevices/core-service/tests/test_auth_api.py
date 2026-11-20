"""Endpoints /api/auth/register, /login e /logout (REQ 01, 03, 04) via HTTP."""
import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_auth_service
from app.main import create_app
from app.security import auth
from app.security.jwt_issuer import JwtTokenIssuer
from app.services.auth_service import AuthService
from tests.fakes import (
    FakeBlacklist,
    FakeHasher,
    FakeRevokedTokens,
    FakeUserRepository,
    fake_transaction,
)

SECRET = "segredo-de-teste-com-mais-de-32-caracteres!!"

ADVOGADO = {
    "nome_completo": "Dr. Fulano da Silva",
    "email": "fulano@exemplo.com.br",
    "senha": "Senha@123",
    "cpf": "123.456.789-09",
    "tipo_perfil": "ADVOGADO",
    "numero_oab": "45.678 / BA",
    "termos_aceitos": True,
}


@pytest.fixture
def client():
    blacklist = FakeBlacklist()
    svc = AuthService(
        FakeUserRepository(), FakeRevokedTokens(blacklist), FakeHasher(),
        JwtTokenIssuer(SECRET, "HS256", 60), fake_transaction,
    )
    verifier = auth.TokenVerifier(SECRET, "HS256", blacklist)
    app = create_app()
    app.dependency_overrides[get_auth_service] = lambda: svc
    app.dependency_overrides[auth.get_token_verifier] = lambda: verifier
    return TestClient(app)


def _login(client, email="fulano@exemplo.com.br", senha="Senha@123"):
    return client.post("/api/auth/login", json={"email": email, "senha": senha})


# ------------------------------------------------------------------ REQ 01
def test_register_lawyer_returns_201_without_password_hash(client):
    r = client.post("/api/auth/register", json=ADVOGADO)
    assert r.status_code == 201
    body = r.json()
    assert body["tipo_perfil"] == "ADVOGADO" and body["numero_oab"] == "45.678 / BA"
    assert "senha" not in body and "senha_hash" not in body


def test_register_common_user_ignores_oab(client):
    r = client.post("/api/auth/register", json={**ADVOGADO, "tipo_perfil": "USUARIO_COMUM"})
    assert r.status_code == 201 and r.json()["numero_oab"] is None


def test_register_without_terms_is_400_with_lgpd_message(client):
    r = client.post("/api/auth/register", json={**ADVOGADO, "termos_aceitos": False})
    assert r.status_code == 400
    assert r.json()["detail"] == "É obrigatório aceitar os Termos de Uso e Política de Privacidade"


def test_register_missing_terms_field_is_also_400(client):
    payload = {k: v for k, v in ADVOGADO.items() if k != "termos_aceitos"}
    assert client.post("/api/auth/register", json=payload).status_code == 400


def test_register_weak_password_is_400(client):
    r = client.post("/api/auth/register", json={**ADVOGADO, "senha": "fraca"})
    assert r.status_code == 400 and "8 caracteres" in r.json()["detail"]


def test_register_lawyer_without_oab_is_400(client):
    r = client.post("/api/auth/register", json={**ADVOGADO, "numero_oab": ""})
    assert r.status_code == 400 and "OAB" in r.json()["detail"]


def test_register_duplicate_email_is_409(client):
    assert client.post("/api/auth/register", json=ADVOGADO).status_code == 201
    assert client.post("/api/auth/register", json=ADVOGADO).status_code == 409


def test_register_duplicate_cpf_is_409(client):
    assert client.post("/api/auth/register", json=ADVOGADO).status_code == 201
    r = client.post("/api/auth/register", json={**ADVOGADO, "email": "outro@exemplo.com.br"})
    assert r.status_code == 409 and "CPF" in r.json()["detail"]


def test_register_invalid_profile_is_422(client):
    r = client.post("/api/auth/register", json={**ADVOGADO, "tipo_perfil": "ADMIN"})
    assert r.status_code == 422


# ------------------------------------------------------------------ REQ 03
def test_login_returns_token_and_user(client):
    client.post("/api/auth/register", json=ADVOGADO)
    r = _login(client)
    assert r.status_code == 200
    body = r.json()
    assert body["token"] and body["token_type"] == "Bearer"
    assert body["user"]["email"] == "fulano@exemplo.com.br"
    assert body["user"]["numero_oab"] == "45.678 / BA"


def test_login_wrong_password_is_401(client):
    client.post("/api/auth/register", json=ADVOGADO)
    r = _login(client, senha="Errada@123")
    assert r.status_code == 401 and r.json()["detail"] == "E-mail ou senha inválidos."


# ------------------------------------------------------------------ REQ 04
def test_logout_revokes_token_and_old_token_gets_401(client):
    client.post("/api/auth/register", json=ADVOGADO)
    token = _login(client).json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/api/auth/logout", headers=headers)
    assert r.status_code == 200 and r.json()["message"] == "Logout realizado e token revogado"

    again = client.post("/api/auth/logout", headers=headers)
    assert again.status_code == 401
    assert again.json()["detail"] == "Sessão encerrada. Faça login novamente"


def test_logout_without_token_is_401(client):
    assert client.post("/api/auth/logout").status_code == 401


def test_auth_endpoints_echo_correlation_id(client):
    r = client.post(
        "/api/auth/login", json={"email": "x@exemplo.com.br", "senha": "a"},
        headers={"X-Correlation-ID": "front-abc"},
    )
    assert r.headers["X-Correlation-ID"] == "front-abc"


def test_cors_allows_portal_web_origin(client):
    r = client.options(
        "/api/auth/login",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"},
    )
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"
