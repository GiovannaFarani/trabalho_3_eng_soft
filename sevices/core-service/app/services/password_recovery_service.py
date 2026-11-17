"""Regra de negócio da recuperação de senha (REQ 02, parte 1 - ADR-005/007).

DIP (Dependency Inversion Principle) - ponto a mostrar ao professor:
este módulo NÃO importa pika/RabbitMQ, nem psycopg2, nem bcrypt, nem FastAPI.
Tudo que é "detalhe" chega pelo construtor como abstração:
  - IMessagePublisher            -> fila (RabbitMQ em produção, fake nos testes)
  - IPasswordResetRepository     -> SQL de password_resets
  - IUserAccountGateway          -> acesso a usuários (UserRepository da Pessoa 1)
  - transaction                  -> context manager de transação
  - hash_password                -> função de hash (bcrypt em produção)
"""
import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Callable, ContextManager, Optional

from app.domain.errors import InvalidResetTokenError, MessagePublishError, WeakPasswordError
from app.domain.password_policy import PASSWORD_RULE_MESSAGE, is_strong_password
from app.logging_config import log_event
from app.messaging.publisher import IMessagePublisher
from app.repositories.password_reset_repository import IPasswordResetRepository
from app.repositories.user_account_gateway import IUserAccountGateway


def _utc_now() -> datetime:
    # A coluna é TIMESTAMP sem fuso: guardamos e comparamos sempre em UTC "ingênuo".
    return datetime.now(timezone.utc).replace(tzinfo=None)


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class PasswordRecoveryService:
    def __init__(
        self,
        users: IUserAccountGateway,
        resets: IPasswordResetRepository,
        publisher: IMessagePublisher,
        transaction: Callable[[], ContextManager],
        hash_password: Callable[[str], str],
        queue_name: str,
        token_ttl_minutes: int = 15,
        clock: Callable[[], datetime] = _utc_now,
        token_factory: Callable[[], str] = lambda: secrets.token_urlsafe(24),
    ) -> None:
        self._users = users
        self._resets = resets
        self._publisher = publisher
        self._transaction = transaction
        self._hash_password = hash_password
        self._queue = queue_name
        self._ttl = timedelta(minutes=token_ttl_minutes)
        self._clock = clock
        self._new_token = token_factory

    # ------------------------------------------------------------------ parte 1
    def request_reset(self, email: str, correlation_id: Optional[str] = None) -> None:
        """Gera o token e publica o pedido de e-mail na fila.

        Nunca revela se o e-mail existe: o chamador responde sempre 200.
        """
        with self._transaction() as cur:
            user = self._users.find_by_email(cur, email.strip())
            if user is None:
                log_event(logging.INFO, "password_reset_requested_unknown_email")
                return
            token = self._new_token()
            self._resets.invalidate_pending(cur, user.id)  # só o último link vale
            self._resets.create(
                cur, user.id, hash_reset_token(token), self._clock() + self._ttl
            )
        # Publica DEPOIS do commit: o worker nunca recebe um token ainda inexistente.
        try:
            self._publisher.publish(
                self._queue,
                {
                    "email": user.email,
                    "nome": user.nome_completo,
                    "resetToken": token,
                    "correlationId": correlation_id,
                },
                correlation_id=correlation_id,
            )
            log_event(
                logging.INFO, "password_reset_message_published",
                queue=self._queue, userId=user.id,
            )
        except MessagePublishError as exc:
            # Resposta continua 200 (não vazar existência da conta); o erro fica no log.
            log_event(
                logging.ERROR, "password_reset_publish_failed",
                queue=self._queue, userId=user.id, error=str(exc),
            )

    # ------------------------------------------------------------------ redefinição
    def reset_password(self, token: str, new_password: str) -> None:
        if not is_strong_password(new_password):
            raise WeakPasswordError(PASSWORD_RULE_MESSAGE)
        new_hash = self._hash_password(new_password)
        with self._transaction() as cur:
            user_id = self._resets.consume_valid(
                cur, hash_reset_token(token.strip()), self._clock()
            )
            if user_id is None:
                raise InvalidResetTokenError("Token inválido, expirado ou já utilizado.")
            self._users.update_password_hash(cur, user_id, new_hash)
        log_event(logging.INFO, "password_reset_completed", userId=user_id)
