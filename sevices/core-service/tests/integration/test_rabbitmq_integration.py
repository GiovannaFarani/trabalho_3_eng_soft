"""Teste de INTEGRAÇÃO com RabbitMQ real: valida o contrato com a Pessoa 3.

    RUN_INTEGRATION=1 pytest tests/integration/test_rabbitmq_integration.py
"""
import json
import os
import uuid

import pika
import pytest

from app.domain.errors import MessagePublishError
from app.messaging.rabbitmq_publisher import RabbitMqPublisher

pytestmark = pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1", reason="defina RUN_INTEGRATION=1 e suba o RabbitMQ"
)
URL = os.getenv("RABBITMQ_URL", "amqp://veridt:veridt_password@localhost:5672/")


def test_message_arrives_persistent_with_contract_and_correlation_id():
    queue = f"test_queue_{uuid.uuid4().hex[:6]}"
    payload = {"email": "a@b.com", "nome": "Maria", "resetToken": "tok", "correlationId": "cid-9"}
    RabbitMqPublisher(URL).publish(queue, payload, correlation_id="cid-9")

    conn = pika.BlockingConnection(pika.URLParameters(URL))
    try:
        ch = conn.channel()
        method, props, body = ch.basic_get(queue, auto_ack=True)
        assert method is not None, "mensagem não chegou na fila"
        assert json.loads(body) == payload
        assert props.delivery_mode == 2                      # persistente
        assert props.correlation_id == "cid-9"
        assert props.headers["x-correlation-id"] == "cid-9"
        ch.queue_delete(queue)
    finally:
        conn.close()


def test_publisher_declares_queue_durable_without_extra_args_matching_contract():
    queue = f"test_queue_{uuid.uuid4().hex[:6]}"
    RabbitMqPublisher(URL).publish(queue, {"x": 1})
    conn = pika.BlockingConnection(pika.URLParameters(URL))
    try:
        ch = conn.channel()
        # Se a Pessoa 3 declarar assim, NÃO haverá PRECONDITION_FAILED:
        ch.queue_declare(queue=queue, durable=True)
        ch.queue_delete(queue)
    finally:
        conn.close()


def test_unreachable_broker_raises_domain_error():
    with pytest.raises(MessagePublishError):
        RabbitMqPublisher("amqp://guest:guest@127.0.0.1:1/", timeout_seconds=1).publish("q", {})
