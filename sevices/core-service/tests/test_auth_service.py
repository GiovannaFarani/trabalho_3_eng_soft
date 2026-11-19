"""Regras de negócio do AuthService (REQ 01, 03, 04) sem banco nem HTTP."""
from dataclasses import replace
from datetime import datetime, timezone

import jwt
import pytest

from app.domain.errors import (
    EmailAlreadyRegisteredError,
    InvalidCpfError,
    InvalidCredentialsError,
    MissingOabError,
    TermsNotAcceptedError,
    WeakPasswordError,
)
from app.security.jwt_issuer import JwtTokenIssuer
from app.services.auth_service import AuthService, RegisterCommand
from tests.fakes import (
    FakeBlacklist,
    FakeHasher,
    FakeRevokedTokens,
    FakeUserRepository,
    fake_transaction,
)

SECRET = "segredo-de-teste-com-mais-de-32-caracteres!!"
NOW = datetime(2026, 11, 19, 12, 0, tzinfo=timezone.utc)

ADVOGADO = RegisterCommand(
    nome_completo="Dra. Maria Souza",
    email="Maria@Exemplo.com.br",
    senha="Senha@123",
    cpf="12345678909",
    tipo_perfil="ADVOGADO",
    numero_oab="12.345 / BA",
    termos_aceitos=True,
)


@pytest.fixture
def ctx():
    users, blacklist = FakeUserRepository(), FakeBlacklist()
    revoked = FakeRevokedTokens(blacklist)
    issuer = JwtTokenIssuer(SECRET, "HS256", 60, clock=lambda: NOW)
    svc = AuthService(users, revoked, FakeHasher(), issuer, fake_transaction)
    return svc, users, revoked


# ------------------------------------------------------------------ REQ 01
def test_register_lawyer_hashes_password_and_normalizes_fields(ctx):
    svc, _, _ = ctx
    user = svc.register(ADVOGADO)
    assert user.email == "maria@exemplo.com.br"
    assert user.senha_hash == "h:Senha@123"
    assert user.cpf == "123.456.789-09"
    assert user.numero_oab == "12.345 / BA"
    assert user.tipo_perfil == "ADVOGADO"


def test_register_requires_terms(ctx):
    svc, *_ = ctx
    with pytest.raises(TermsNotAcceptedError):
        svc.register(replace(ADVOGADO, termos_aceitos=False))


@pytest.mark.parametrize("senha", ["curta@1", "semsimbolo123", "SemNumero@", "12345678@"])
def test_register_rejects_weak_password(ctx, senha):
    svc, *_ = ctx
    with pytest.raises(WeakPasswordError):
        svc.register(replace(ADVOGADO, senha=senha))


@pytest.mark.parametrize("oab", [None, "", "   "])
def test_lawyer_without_oab_is_rejected_decision_d1(ctx, oab):
    svc, *_ = ctx
    with pytest.raises(MissingOabError):
        svc.register(replace(ADVOGADO, numero_oab=oab))


def test_common_user_has_oab_forced_to_null_decision_d1(ctx):
    svc, *_ = ctx
    user = svc.register(replace(ADVOGADO, tipo_perfil="USUARIO_COMUM", numero_oab="99.999 / SP"))
    assert user.numero_oab is None


def test_register_rejects_invalid_cpf(ctx):
    svc, *_ = ctx
    with pytest.raises(InvalidCpfError):
        svc.register(replace(ADVOGADO, cpf="123.456.789"))


def test_register_duplicate_email_is_rejected_case_insensitive(ctx):
    svc, *_ = ctx
    svc.register(ADVOGADO)
    with pytest.raises(EmailAlreadyRegisteredError):
        svc.register(replace(ADVOGADO, email="MARIA@exemplo.com.br"))


# ------------------------------------------------------------------ REQ 03
def test_login_issues_jwt_with_expected_claims_and_1h_expiry(ctx):
    svc, *_ = ctx
    created = svc.register(ADVOGADO)
    result = svc.login("maria@exemplo.com.br", "Senha@123")
    claims = jwt.decode(result.token, SECRET, algorithms=["HS256"], options={"verify_exp": False})
    assert claims["sub"] == created.id
    assert claims["nome"] == "Dra. Maria Souza"
    assert claims["email"] == "maria@exemplo.com.br"
    assert claims["role"] == "ADVOGADO"
    assert claims["oab"] == "12.345 / BA"
    assert claims["exp"] - int(NOW.timestamp()) == 3600
    assert result.user.id == created.id


@pytest.mark.parametrize("email,senha", [
    ("maria@exemplo.com.br", "Errada@123"),
    ("ninguem@exemplo.com.br", "Senha@123"),
])
def test_login_wrong_password_or_unknown_email_gives_same_error(ctx, email, senha):
    svc, *_ = ctx
    svc.register(ADVOGADO)
    with pytest.raises(InvalidCredentialsError) as exc:
        svc.login(email, senha)
    assert str(exc.value) == "E-mail ou senha inválidos."


# ------------------------------------------------------------------ REQ 04
def test_logout_revokes_token_until_its_expiration(ctx):
    svc, _, revoked = ctx
    svc.register(ADVOGADO)
    token = svc.login("maria@exemplo.com.br", "Senha@123").token
    svc.logout(token, "qualquer")
    assert token in revoked.blacklist.revoked
    assert revoked.expirations[token] == datetime(2026, 11, 19, 13, 0)  # UTC, sem fuso
