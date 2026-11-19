
import logging

from app.config import get_settings
from app.notifications.email_sender import EmailSender
from app.notifications.password_recovery_handler import (
    PasswordRecoveryHandler,
)
from app.notifications.rabbitmq_consumer import RabbitMQConsumer


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    settings = get_settings()

    email_sender = EmailSender(
        host=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        sender=settings.smtp_from,
    )

    handler = PasswordRecoveryHandler(
        email_sender=email_sender,
        frontend_reset_url=settings.frontend_reset_url,
    )

    consumer = RabbitMQConsumer(
        rabbitmq_url=settings.rabbitmq_url,
        handler=handler,
    )

    logging.info("Iniciando Evidence Service Consumer...")

    consumer.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Consumidor encerrado pelo usuário.")
