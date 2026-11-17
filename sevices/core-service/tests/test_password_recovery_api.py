import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_password_recovery_service
from app.main import create_app
from app.services.password_recovery_service import PasswordRecoveryService
from tests.fakes import FakePublisher, FakeResets, FakeUsers, fake_transaction


@pytest.fixture
def ctx():
    users, resets, pub = FakeUsers(), FakeResets(), FakePublisher()
    svc = PasswordRecoveryService(
        users, resets, pub, fake_transaction, lambda p: "h:" + p, "password_recovery_queue"
    )
    app = create_app()
    app.dependency_overrides[get_password_recovery_service] = lambda: svc
    return TestClient(app), users, resets, pub


def test_forgot_password_known_and_unknown_email_look_identical(ctx):
    client, _, _, pub = ctx
    a = client.post("/api/auth/forgot-password", json={"email": "fulano@exemplo.com.br"})
    b = client.post("/api/auth/forgot-password", json={"email": "ninguem@exemplo.com.br"})
    assert a.status_code == b.status_code == 200
    assert a.json() == b.json()
    assert len(pub.messages) == 1


def test_forgot_password_propagates_correlation_id_to_the_queue_message(ctx):
    client, _, _, pub = ctx
    r = client.post(
        "/api/auth/forgot-password", json={"email": "fulano@exemplo.com.br"},
        headers={"X-Correlation-ID": "front-123"},
    )
    assert r.headers["X-Correlation-ID"] == "front-123"
    assert pub.messages[0]["payload"]["correlationId"] == "front-123"


def test_forgot_password_invalid_email_format_is_422(ctx):
    client, *_ = ctx
    assert client.post("/api/auth/forgot-password", json={"email": "nao-e-email"}).status_code == 422


def test_full_flow_reset_password(ctx):
    client, users, _, pub = ctx
    client.post("/api/auth/forgot-password", json={"email": "fulano@exemplo.com.br"})
    token = pub.messages[0]["payload"]["resetToken"]
    ok = client.post("/api/auth/reset-password", json={"token": token, "nova_senha": "Nova@1234"})
    assert ok.status_code == 200
    assert users.password_hashes["u-1"] == "h:Nova@1234"
    again = client.post("/api/auth/reset-password", json={"token": token, "nova_senha": "Nova@1234"})
    assert again.status_code == 400


def test_reset_with_weak_password_is_400(ctx):
    client, *_ = ctx
    r = client.post("/api/auth/reset-password", json={"token": "x", "nova_senha": "fraca"})
    assert r.status_code == 400 and "8 caracteres" in r.json()["detail"]


def test_reset_with_invalid_token_is_400(ctx):
    client, *_ = ctx
    r = client.post("/api/auth/reset-password", json={"token": "x", "nova_senha": "Nova@1234"})
    assert r.status_code == 400
