
import logging
from typing import Any, Dict
from urllib.parse import urlencode, urlsplit, urlunsplit

from app.notifications.email_sender import EmailSender


logger = logging.getLogger(__name__)


class PasswordRecoveryHandler:
    def __init__(
        self,
        email_sender: EmailSender,
        frontend_reset_url: str,
    ) -> None:
        self._email_sender = email_sender
        self._frontend_reset_url = frontend_reset_url

    def handle(self, payload: Dict[str, Any]) -> None:
        """Processa uma solicitação de recuperação de senha."""

        required_fields = ("email", "nome", "resetToken")

        for field in required_fields:
            value = payload.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"Campo obrigatório inválido na mensagem: {field}"
                )

        email = payload["email"].strip()
        nome = payload["nome"].strip()
        token = payload["resetToken"].strip()
        correlation_id = payload.get("correlationId")

        if correlation_id is not None and not isinstance(
            correlation_id, str
        ):
            raise ValueError("Campo correlationId inválido.")

        # Adiciona o token à URL sem perder parâmetros existentes.
        parts = urlsplit(self._frontend_reset_url)

        query = parts.query
        token_query = urlencode({"token": token})

        if query:
            query = f"{query}&{token_query}"
        else:
            query = token_query

        reset_url = urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                parts.path,
                query,
                parts.fragment,
            )
        )

        self._email_sender.send_password_recovery(
            to_email=email,
            nome=nome,
            reset_url=reset_url,
        )

        logger.info(
            "E-mail de recuperação enviado. correlation_id=%s",
            correlation_id,
        )
