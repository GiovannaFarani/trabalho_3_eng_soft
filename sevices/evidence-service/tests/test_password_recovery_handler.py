
from unittest.mock import Mock

import pytest

from app.notifications.password_recovery_handler import (
    PasswordRecoveryHandler,
)


def test_processar_recuperacao_de_senha():
    email_sender = Mock()

    handler = PasswordRecoveryHandler(
        email_sender=email_sender,
        frontend_reset_url="http://localhost:3000/reset-password",
    )

    payload = {
        "email": "teste@email.com",
        "nome": "Usuario Teste",
        "resetToken": "token-teste-123",
        "correlationId": "correlation-123",
    }

    handler.handle(payload)

    email_sender.send_password_recovery.assert_called_once_with(
        to_email="teste@email.com",
        nome="Usuario Teste",
        reset_url=(
            "http://localhost:3000/reset-password"
            "?token=token-teste-123"
        ),
    )


def test_rejeitar_mensagem_sem_token():
    email_sender = Mock()

    handler = PasswordRecoveryHandler(
        email_sender=email_sender,
        frontend_reset_url="http://localhost:3000/reset-password",
    )

    payload = {
        "email": "teste@email.com",
        "nome": "Usuario Teste",
    }

    with pytest.raises(ValueError):
        handler.handle(payload)

    email_sender.send_password_recovery.assert_not_called()


def test_rejeitar_email_invalido():
    email_sender = Mock()

    handler = PasswordRecoveryHandler(
        email_sender=email_sender,
        frontend_reset_url="http://localhost:3000/reset-password",
    )

    payload = {
        "email": "",
        "nome": "Usuario Teste",
        "resetToken": "token-teste-123",
        "correlationId": None,
    }

    with pytest.raises(ValueError):
        handler.handle(payload)

    email_sender.send_password_recovery.assert_not_called()
