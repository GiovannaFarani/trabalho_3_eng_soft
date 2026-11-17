"""Implementação RabbitMQ de IMessagePublisher (ADR-007). É o ÚNICO arquivo que
conhece o pika.

CONTRATO COM A PESSOA 3 (consumidor):
  - fila: `password_recovery_queue`, durable=True, SEM argumentos extras
    (a Pessoa 3 deve declarar exatamente igual, senão o RabbitMQ responde
    PRECONDITION_FAILED);
  - corpo: JSON UTF-8 {"email","nome","resetToken","correlationId"};
  - mensagens persistentes (delivery_mode=2) e com publisher confirms;
  - o correlationId também vai nas propriedades da mensagem (correlation_id)
    e no header `x-correlation-id`.

Abre uma conexão por publicação: a pika.BlockingConnection não é thread-safe e
recuperação de senha é um fluxo de baixa frequência, então simplicidade e
robustez valem mais que otimização.
"""
import json
from typing import Any, Dict, Optional

import pika
from pika.exceptions import AMQPError

from app.domain.errors import MessagePublishError
from app.messaging.publisher import IMessagePublisher


class RabbitMqPublisher(IMessagePublisher):
    def __init__(self, url: str, timeout_seconds: float = 5.0) -> None:
        self._url = url
        self._timeout = timeout_seconds

    def publish(
        self, queue: str, payload: Dict[str, Any], correlation_id: Optional[str] = None
    ) -> None:
        params = pika.URLParameters(self._url)
        params.socket_timeout = self._timeout
        params.connection_attempts = 1  # sem retries aqui: quem faz retry é o fluxo chamador
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {"x-correlation-id": correlation_id} if correlation_id else None
        try:
            connection = pika.BlockingConnection(params)
            try:
                channel = connection.channel()
                channel.queue_declare(queue=queue, durable=True)
                channel.confirm_delivery()
                channel.basic_publish(
                    exchange="",
                    routing_key=queue,
                    body=body,
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        delivery_mode=2,
                        correlation_id=correlation_id,
                        headers=headers,
                    ),
                    mandatory=True,
                )
            finally:
                if connection.is_open:
                    connection.close()
        except (AMQPError, OSError) as exc:
            raise MessagePublishError(f"Falha ao publicar na fila '{queue}': {exc}") from exc
