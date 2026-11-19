
import logging
import sys

from app.config import get_settings
from app.notifications.rabbitmq_consumer import RabbitMQConsumer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)


class FakeHandler:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.calls = 0

    def handle(self, payload):
        self.calls += 1

        print(
            f"Handler executado: tentativa {self.calls} "
            f"| correlationId={payload.get('correlationId')}"
        )

        if self.should_fail:
            raise RuntimeError("Falha simulada para teste de Retry/DLQ")

        print("Mensagem processada com sucesso pelo handler simulado.")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "success"

    if mode not in ("success", "fail"):
        raise ValueError("Use success ou fail.")

    handler = FakeHandler(should_fail=(mode == "fail"))

    consumer = RabbitMQConsumer(
        rabbitmq_url=get_settings().rabbitmq_url,
        handler=handler,
    )

    print(f"Iniciando teste manual: {mode}")
    consumer.start()


if __name__ == "__main__":
    main()
