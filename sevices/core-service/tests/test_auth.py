import time

import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.security import auth
from tests.fakes import FakeBlacklist

SECRET = "segredo-de-teste-com-mais-de-32-caracteres!!"


def make_token(role="ADVOGADO", exp_delta=3600, secret=SECRET, alg="HS256", **extra):
    claims = {"sub": "user-1", "nome": "Dr. Fulano", "email": "f@x.com", "role": role, "oab": "45.678/BA",
              "exp": int(time.time()) + exp_delta, **extra}
    return jwt.encode(claims, secret, algorithm=alg)


def make_client(revoked=()):
    app = FastAPI()
    verifier = auth.TokenVerifier(SECRET, "HS256", FakeBlacklist(revoked))
    app.dependency_overrides[auth.get_token_verifier] = lambda: verifier

    @app.get("/me")
    def me(user: auth.AuthenticatedUser = Depends(auth.get_current_user)):
        return {"id": user.id, "role": user.role, "oab": user.oab}

    @app.get("/advogados")
    def only_lawyers(user=Depends(auth.require_roles("ADVOGADO"))):
        return {"ok": True}

    return TestClient(app)


def bearer(t):
    return {"Authorization": f"Bearer {t}"}


def test_missing_token_is_401():
    assert make_client().get("/me").status_code == 401


def test_valid_token_returns_user_from_claims():
    r = make_client().get("/me", headers=bearer(make_token()))
    assert r.status_code == 200 and r.json() == {"id": "user-1", "role": "ADVOGADO", "oab": "45.678/BA"}


def test_invalid_signature_is_401():
    assert make_client().get("/me", headers=bearer(make_token(secret="x" * 40))).status_code == 401


def test_expired_token_is_401():
    assert make_client().get("/me", headers=bearer(make_token(exp_delta=-10))).status_code == 401


def test_token_without_exp_is_401():
    t = jwt.encode({"sub": "u", "role": "ADVOGADO"}, SECRET, algorithm="HS256")
    assert make_client().get("/me", headers=bearer(t)).status_code == 401


def test_alg_none_token_is_rejected():
    t = jwt.encode({"sub": "u", "role": "ADVOGADO", "exp": int(time.time()) + 99}, None, algorithm="none")
    assert make_client().get("/me", headers=bearer(t)).status_code == 401


def test_revoked_token_is_401_with_logout_message():
    token = make_token()
    r = make_client(revoked={token}).get("/me", headers=bearer(token))
    assert r.status_code == 401 and r.json()["detail"] == "Sessão encerrada. Faça login novamente"


def test_rbac_allows_and_denies_by_role():
    c = make_client()
    assert c.get("/advogados", headers=bearer(make_token("ADVOGADO"))).status_code == 200
    assert c.get("/advogados", headers=bearer(make_token("USUARIO_COMUM"))).status_code == 403
