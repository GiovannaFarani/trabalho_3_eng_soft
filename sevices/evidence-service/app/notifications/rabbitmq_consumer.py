
import json
import logging
import time

import pika
from pika.exceptions import AMQPError

from app.notifications.password_recovery_handler import (
    PasswordRecoveryHandler,
)


logger = logging.getLogger(__name__)

QUEUE_NAME = "password_recovery_queue"
DLQ_NAME = "password_recovery_dlq"

MAX_ATTEMPTS = 3
RETRY_INTERVAL = 2


class RabbitMQConsumer:
    def __init__(
        self,
        rabbitmq_url: str,
        handler: PasswordRecoveryHandler,
    ) -> None:
        self._rabbitmq_url = rabbitmq_url
        self._handler = handler

    def start(self) -> None:
        """Conecta ao RabbitMQ e inicia o consumo das mensagens."""

        params = pika.URLParameters(self._rabbitmq_url)
        params.connection_attempts = 3
        params.retry_delay = 5
        params.heartbeat = 60

        connection = pika.BlockingConnection(params)

        try:
            channel = connection.channel()

            # Declara as filas duráveis.
            channel.queue_declare(
                queue=QUEUE_NAME,
                durable=True,
            )

            channel.queue_declare(
                queue=DLQ_NAME,
                durable=True,
            )

            # Habilita confirmação das publicações.
            channel.confirm_delivery()

            # Processa uma mensagem por vez.
            channel.basic_qos(prefetch_count=1)

            def send_to_dlq(body, properties, correlation_id):
                """Publica a mensagem na DLQ com confirmação."""

                dlq_properties = pika.BasicProperties(
                    delivery_mode=2,
                    content_type=(
                        properties.content_type
                        if properties else "application/json"
                    ),
                    correlation_id=correlation_id,
                )

                channel.basic_publish(
                    exchange="",
                    routing_key=DLQ_NAME,
                    body=body,
                    properties=dlq_properties,
                    mandatory=True,
                )

                logger.error(
                    "Mensagem encaminhada para DLQ. correlationId=%s",
                    correlation_id,
                )

            def callback(ch, method, properties, body):
                correlation_id = (
                    properties.correlation_id
                    if properties and properties.correlation_id
                    else "não informado"
                )

                # Validação do conteúdo da mensagem.
                try:
                    payload = json.loads(body.decode("utf-8"))

                    if not isinstance(payload, dict):
                        raise ValueError(
                            "O corpo da mensagem deve ser um objeto JSON."
                        )

                except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
                    logger.exception(
                        "Mensagem inválida. correlationId=%s",
                        correlation_id,
                    )

                    try:
                        send_to_dlq(body, properties, correlation_id)

                        ch.basic_ack(
                            delivery_tag=method.delivery_tag,
                        )

                    except AMQPError:
                        logger.exception(
                            "Falha ao publicar mensagem inválida na DLQ."
                        )

                        ch.basic_nack(
                            delivery_tag=method.delivery_tag,
                            requeue=True,
                        )

                        ch.stop_consuming()

                    return
                correlation_id = (
                    (properties.correlation_id if properties else none)
                    or payload.get("correlationId")
                    or "não informado"
                )

                # Processamento com até três tentativas.
                for attempt in range(1, MAX_ATTEMPTS + 1):
                    try:
                        logger.info(
                            "Processando mensagem. Tentativa %s/%s. "
                            "correlationId=%s",
                            attempt,
                            MAX_ATTEMPTS,
                            correlation_id,
                        )

                        self._handler.handle(payload)

                        logger.info(
                            "Mensagem processada com sucesso. "
                            "correlationId=%s",
                            correlation_id,
                        )

                        ch.basic_ack(
                            delivery_tag=method.delivery_tag,
                        )

                        return

                    except Exception:
                        logger.exception(
                            "Falha no processamento. Tentativa %s/%s. "
                            "correlationId=%s",
                            attempt,
                            MAX_ATTEMPTS,
                            correlation_id,
                        )

                        if attempt < MAX_ATTEMPTS:
                            logger.info(
                                "Nova tentativa em %s segundos. "
                                "correlationId=%s",
                                RETRY_INTERVAL,
                                correlation_id,
                            )

                            time.sleep(RETRY_INTERVAL)

                # Todas as tentativas falharam.
                try:
                    send_to_dlq(body, properties, correlation_id)

                    ch.basic_ack(
                        delivery_tag=method.delivery_tag,
                    )

                except AMQPError:
                    logger.exception(
                        "Não foi possível publicar na DLQ. "
                        "A mensagem será devolvida à fila principal. "
                        "correlationId=%s",
                        correlation_id,
                    )

                    ch.basic_nack(
                        delivery_tag=method.delivery_tag,
                        requeue=True,
                    )

                    ch.stop_consuming()

            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=callback,
                auto_ack=False,
            )

            logger.info(
                "Consumidor iniciado. Aguardando mensagens na fila %s.",
                QUEUE_NAME,
            )

            channel.start_consuming()

        finally:
            if connection.is_open:
                connection.close()
