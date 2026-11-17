"""Dublês de teste (fakes) em memória para as abstrações do projeto."""
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from app.domain.errors import MessagePublishError
from app.messaging.publisher import IMessagePublisher
from app.repositories.password_reset_repository import IPasswordResetRepository
from app.repositories.user_account_gateway import IUserAccountGateway, UserAccount
from app.security.token_blacklist import ITokenBlacklist


class FakePublisher(IMessagePublisher):
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.messages: List[Dict[str, Any]] = []

    def publish(self, queue, payload, correlation_id=None):
        if self.fail:
            raise MessagePublishError("broker fora do ar")
        self.messages.append({"queue": queue, "payload": payload, "correlation_id": correlation_id})


class FakeUsers(IUserAccountGateway):
    def __init__(self) -> None:
        self.by_email = {"fulano@exemplo.com.br": UserAccount("u-1", "Dr. Fulano da Silva", "fulano@exemplo.com.br")}
        self.password_hashes: Dict[str, str] = {}

    def find_by_email(self, cur, email) -> Optional[UserAccount]:
        return self.by_email.get(email.lower())

    def update_password_hash(self, cur, user_id, password_hash) -> None:
        self.password_hashes[user_id] = password_hash


class FakeResets(IPasswordResetRepository):
    def __init__(self) -> None:
        self.rows: List[Dict[str, Any]] = []

    def invalidate_pending(self, cur, user_id) -> None:
        for r in self.rows:
            if r["user_id"] == user_id:
                r["used"] = True

    def create(self, cur, user_id, token_hash, expires_at) -> None:
        self.rows.append({"user_id": user_id, "token_hash": token_hash, "expires_at": expires_at, "used": False})

    def consume_valid(self, cur, token_hash, now):
        for r in self.rows:
            if r["token_hash"] == token_hash and not r["used"] and r["expires_at"] > now:
                r["used"] = True
                return r["user_id"]
        return None


@contextmanager
def fake_transaction():
    yield None


class FakeBlacklist(ITokenBlacklist):
    def __init__(self, revoked=()) -> None:
        self.revoked = set(revoked)

    def is_revoked(self, token: str) -> bool:
        return token in self.revoked
