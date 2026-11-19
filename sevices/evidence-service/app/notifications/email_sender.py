
import smtplib
import ssl
from email.message import EmailMessage
from html import escape


class EmailSender:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        sender: str,
    ) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._sender = sender

    def send_password_recovery(
        self,
        to_email: str,
        nome: str,
        reset_url: str,
    ) -> None:
        message = EmailMessage()
        message["Subject"] = "Recuperação de senha - Veridt"
        message["From"] = self._sender
        message["To"] = to_email

        nome_seguro = escape(nome or "Usuário")
        url_segura = escape(reset_url, quote=True)

        message.set_content(
            f"""Olá, {nome or 'Usuário'}!

Recebemos uma solicitação para redefinir sua senha.

Para criar uma nova senha, acesse o link abaixo:

{reset_url}

Se você não solicitou essa alteração, ignore este e-mail.

Por segurança, o link possui prazo de validade.
"""
        )

        message.add_alternative(
            f"""\
<html>
    <body>
        <p>Olá, {nome_seguro}!</p>
        <p>Recebemos uma solicitação para redefinir sua senha.</p>
        <p>
            <a href="{url_segura}">Redefinir minha senha</a>
        </p>
        <p>
            Se você não solicitou essa alteração, ignore este e-mail.
        </p>
        <p>Por segurança, o link possui prazo de validade.</p>
        <p>Equipe Veridt</p>
    </body>
</html>
""",
            subtype="html",
        )

        contexto = ssl.create_default_context()

        with smtplib.SMTP(
            self._host,
            self._port,
            timeout=15,
        ) as servidor:
            servidor.ehlo()
            servidor.starttls(context=contexto)
            servidor.ehlo()
            servidor.login(self._username, self._password)
            servidor.send_message(message)
