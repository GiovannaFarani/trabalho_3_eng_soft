"""Abstração de publicação de mensagens (DIP - Dependency Inversion Principle).

O PasswordRecoveryService depende DESTA interface, nunca de pika/RabbitMQ.
Trocar RabbitMQ por Redis/SQS (ou por um fake nos testes) não exige mexer na
regra de negócio.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IMessagePublisher(ABC):
    @abstractmethod
    def publish(
        self, queue: str, payload: Dict[str, Any], correlation_id: Optional[str] = None
    ) -> None:
        """Publica `payload` (JSON) na fila `queue`.

        Levanta MessagePublishError se não for possível entregar ao broker.
        """
