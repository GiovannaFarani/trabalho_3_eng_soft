"""Garante que a cópia da segurança funciona no evidence-service (REQ 12 / ADR-010)."""
import json
import logging
import time

import jwt
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.logging_config import configure_logging
from app.middleware.correlation_id import CorrelationIdMiddleware
from app.security import auth
from app.security.token_blacklist import ITokenBlacklist

SECRET = "segredo-de-teste-com-mais-de-32-caracteres!!"


class Blacklist(ITokenBlacklist):
    def __init__(self, revoked=()):
        self.revoked = set(revoked)

    def is_revoked(self, token):
        return token in self.revoked


def make_app(revoked=()):
    configure_logging("evidence-service")
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)
    verifier = auth.TokenVerifier(SECRET, "HS256", Blacklist(revoked))
    app.dependency_overrides[auth.get_token_verifier] = lambda: verifier

    @app.get("/api/records")
    def records(user: auth.AuthenticatedUser = Depends(auth.get_current_user)):
        return {"tenant": user.id}

    return TestClient(app)


def tok(sub="user-A"):
    return jwt.encode({"sub": sub, "role": "ADVOGADO", "exp": int(time.time()) + 600}, SECRET, algorithm="HS256")


def test_tenant_id_comes_from_token_not_from_request():
    c = make_app()
    r = c.get("/api/records?userId=user-B", headers={"Authorization": f"Bearer {tok('user-A')}"})
    assert r.json() == {"tenant": "user-A"}


def test_revoked_token_blocked_in_evidence_service():
    t = tok()
    r = make_app(revoked={t}).get("/api/records", headers={"Authorization": f"Bearer {t}"})
    assert r.status_code == 401


def test_logs_use_evidence_service_name_and_same_correlation_id(caplog):
    caplog.set_level(logging.INFO)
    make_app().get("/api/records", headers={"X-Correlation-ID": "corr-demo-001"})
    logs = [json.loads(r.getMessage()) for r in caplog.records if r.name == "veridt"]
    assert logs[-1]["service"] == "evidence-service" and logs[-1]["correlationId"] == "corr-demo-001"
