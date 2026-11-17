from datetime import datetime, timedelta

import pytest

from app.domain.errors import InvalidResetTokenError, WeakPasswordError
from app.services.password_recovery_service import PasswordRecoveryService, hash_reset_token
from tests.fakes import FakePublisher, FakeResets, FakeUsers, fake_transaction

NOW = datetime(2026, 11, 17, 12, 0, 0)
STRONG = "Senha@123"


class Clock:
    def __init__(self):
        self.now = NOW

    def __call__(self):
        return self.now


def make(publisher=None, tokens=None):
    users, resets = FakeUsers(), FakeResets()
    publisher = publisher or FakePublisher()
    clock = Clock()
    seq = iter(tokens or ["tok-1", "tok-2", "tok-3"])
    svc = PasswordRecoveryService(
        users=users, resets=resets, publisher=publisher, transaction=fake_transaction,
        hash_password=lambda p: f"hash({p})", queue_name="password_recovery_queue",
        token_ttl_minutes=15, clock=clock, token_factory=lambda: next(seq),
    )
    return svc, users, resets, publisher, clock


def test_unknown_email_does_nothing_and_does_not_raise():
    svc, _, resets, pub, _ = make()
    svc.request_reset("naoexiste@x.com", "cid-1")
    assert resets.rows == [] and pub.messages == []


def test_known_email_stores_hashed_token_with_15min_ttl_and_publishes_contract():
    svc, _, resets, pub, _ = make()
    svc.request_reset("FULANO@exemplo.com.br", "cid-42")
    row = resets.rows[0]
    assert row["token_hash"] == hash_reset_token("tok-1") != "tok-1"
    assert row["expires_at"] == NOW + timedelta(minutes=15)
    msg = pub.messages[0]
    assert msg["queue"] == "password_recovery_queue"
    assert msg["payload"] == {
        "email": "fulano@exemplo.com.br", "nome": "Dr. Fulano da Silva",
        "resetToken": "tok-1", "correlationId": "cid-42",
    }
    assert msg["correlation_id"] == "cid-42"


def test_new_request_invalidates_previous_token():
    svc, _, resets, _, _ = make()
    svc.request_reset("fulano@exemplo.com.br")
    svc.request_reset("fulano@exemplo.com.br")
    assert [r["used"] for r in resets.rows] == [True, False]
    with pytest.raises(InvalidResetTokenError):
        svc.reset_password("tok-1", STRONG)
    svc.reset_password("tok-2", STRONG)


def test_publish_failure_does_not_raise_but_token_was_saved():
    svc, _, resets, _, _ = make(publisher=FakePublisher(fail=True))
    svc.request_reset("fulano@exemplo.com.br")  # não levanta
    assert len(resets.rows) == 1


def test_reset_updates_hash_and_token_is_single_use():
    svc, users, _, _, _ = make()
    svc.request_reset("fulano@exemplo.com.br")
    svc.reset_password("tok-1", STRONG)
    assert users.password_hashes["u-1"] == f"hash({STRONG})"
    with pytest.raises(InvalidResetTokenError):
        svc.reset_password("tok-1", STRONG)


def test_expired_token_is_rejected():
    svc, users, _, _, clock = make()
    svc.request_reset("fulano@exemplo.com.br")
    clock.now = NOW + timedelta(minutes=15, seconds=1)
    with pytest.raises(InvalidResetTokenError):
        svc.reset_password("tok-1", STRONG)
    assert users.password_hashes == {}


@pytest.mark.parametrize("weak", ["curta1@", "semnumeros@@", "semsimbolo123", "12345678@@", "Senha 123@"])
def test_weak_password_rejected_and_token_not_consumed(weak):
    svc, _, resets, _, _ = make()
    svc.request_reset("fulano@exemplo.com.br")
    with pytest.raises(WeakPasswordError):
        svc.reset_password("tok-1", weak)
    assert resets.rows[0]["used"] is False


def test_unknown_token_rejected():
    svc, *_ = make()
    with pytest.raises(InvalidResetTokenError):
        svc.reset_password("inexistente", STRONG)
