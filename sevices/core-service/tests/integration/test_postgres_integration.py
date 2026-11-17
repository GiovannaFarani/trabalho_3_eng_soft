"""Testes de INTEGRAÇÃO com PostgreSQL real (schema do init.sql da equipe).

Rodar (com `docker compose up -d` ativo):
    RUN_INTEGRATION=1 DATABASE_URL=postgresql://veridt:veridt_password@localhost:5432/veridt_db pytest tests/integration
"""
import os
import time
import uuid

import bcrypt
import jwt
import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.db import Database
from app.security import auth
from app.security.token_blacklist import PostgresTokenBlacklist
from app.repositories.password_reset_repository import PgPasswordResetRepository
from app.repositories.user_account_gateway import PgUserAccountGateway
from app.services.password_recovery_service import PasswordRecoveryService
from tests.fakes import FakePublisher

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1", reason="defina RUN_INTEGRATION=1 e suba o Postgres"
)


@pytest.fixture(scope="module")
def db():
    database = Database(os.environ["DATABASE_URL"])
    yield database
    database.close()


@pytest.fixture
def user(db):
    email = f"it-{uuid.uuid4().hex[:8]}@exemplo.com.br"
    old_hash = bcrypt.hashpw(b"Antiga@123", bcrypt.gensalt()).decode()
    with db.transaction() as cur:
        cur.execute(
            "INSERT INTO users (nome_completo,email,senha_hash,cpf,tipo_perfil) "
            "VALUES ('Teste Integração',%s,%s,'123.456.789-09','USUARIO_COMUM') RETURNING id",
            (email, old_hash),
        )
        uid = str(cur.fetchone()["id"])
    yield {"id": uid, "email": email}
    with db.transaction() as cur:
        cur.execute("DELETE FROM users WHERE id = %s", (uid,))


def make_service(db, publisher):
    return PasswordRecoveryService(
        PgUserAccountGateway(), PgPasswordResetRepository(), publisher, db.transaction,
        lambda p: bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode(), "password_recovery_queue",
    )


def test_full_recovery_flow_against_real_postgres(db, user):
    pub = FakePublisher()
    svc = make_service(db, pub)
    svc.request_reset(user["email"].upper(), "cid-it-1")  # case-insensitive
    payload = pub.messages[0]["payload"]
    token = payload["resetToken"]

    with db.transaction() as cur:
        cur.execute("SELECT reset_token, used, expires_at FROM password_resets WHERE user_id=%s", (user["id"],))
        row = cur.fetchone()
    assert row["reset_token"] != token and len(row["reset_token"]) == 64 and row["used"] is False

    svc.reset_password(token, "Nova@12345")
    with db.transaction() as cur:
        cur.execute("SELECT senha_hash FROM users WHERE id=%s", (user["id"],))
        new_hash = cur.fetchone()["senha_hash"]
    assert bcrypt.checkpw(b"Nova@12345", new_hash.encode())
    assert not bcrypt.checkpw(b"Antiga@123", new_hash.encode())


def test_token_cannot_be_consumed_twice_and_expired_is_rejected(db, user):
    from datetime import datetime, timedelta
    from app.domain.errors import InvalidResetTokenError
    repo = PgPasswordResetRepository()
    now = datetime.utcnow()
    with db.transaction() as cur:
        repo.create(cur, user["id"], "a" * 64, now + timedelta(minutes=15))
        repo.create(cur, user["id"], "b" * 64, now - timedelta(minutes=1))
    with db.transaction() as cur:
        assert repo.consume_valid(cur, "a" * 64, now) == user["id"]
    with db.transaction() as cur:
        assert repo.consume_valid(cur, "a" * 64, now) is None   # já usado
        assert repo.consume_valid(cur, "b" * 64, now) is None   # expirado


def test_transaction_rolls_back_on_error(db, user):
    from app.domain.errors import InvalidResetTokenError
    svc = make_service(db, FakePublisher())
    with pytest.raises(InvalidResetTokenError):
        svc.reset_password("nao-existe", "Nova@12345")
    with db.transaction() as cur:
        cur.execute("SELECT senha_hash FROM users WHERE id=%s", (user["id"],))
        assert bcrypt.checkpw(b"Antiga@123", cur.fetchone()["senha_hash"].encode())


def test_blacklist_reads_revoked_tokens_table(db):
    secret = os.environ["JWT_SECRET"]
    token = jwt.encode({"sub": "u", "role": "ADVOGADO", "exp": int(time.time()) + 600}, secret, algorithm="HS256")
    verifier = auth.TokenVerifier(secret, "HS256", PostgresTokenBlacklist(db))
    app = FastAPI()
    app.dependency_overrides[auth.get_token_verifier] = lambda: verifier

    @app.get("/me")
    def me(u=Depends(auth.get_current_user)):
        return {"id": u.id}

    client = TestClient(app)
    h = {"Authorization": f"Bearer {token}"}
    assert client.get("/me", headers=h).status_code == 200
    with db.transaction() as cur:  # o que a Pessoa 1 faz no logout
        cur.execute("INSERT INTO revoked_tokens (token, expires_at) VALUES (%s, NOW() + interval '1 hour')", (token,))
    try:
        r = client.get("/me", headers=h)
        assert r.status_code == 401 and "Sessão encerrada" in r.json()["detail"]
    finally:
        with db.transaction() as cur:
            cur.execute("DELETE FROM revoked_tokens WHERE token=%s", (token,))
