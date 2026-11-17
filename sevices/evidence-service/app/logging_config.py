"""Logging estruturado em JSON (ADR-009).

Cada linha impressa no terminal é um objeto JSON com, no mínimo:
timestamp, level, service, correlationId e event. O correlationId vem de uma
ContextVar preenchida pelo CorrelationIdMiddleware, então qualquer código que
rode durante a requisição (service, repository...) loga com o mesmo ID sem
precisar recebê-lo como parâmetro.
"""
import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Optional

correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)

_LOGGER_NAME = "veridt"
_service_name = "unknown-service"


def get_correlation_id() -> Optional[str]:
    return correlation_id_var.get()


def configure_logging(service_name: str) -> None:
    """Instala (uma única vez) um handler que imprime só a mensagem JSON."""
    global _service_name
    _service_name = service_name
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    if not any(getattr(h, "_veridt", False) for h in logger.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        handler._veridt = True  # type: ignore[attr-defined]
        logger.addHandler(handler)


def log_event(level: int, event: str, **fields) -> None:
    """Emite um log JSON estruturado já com service e correlationId."""
    record = {
        "timestamp": datetime.now(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z"),
        "level": logging.getLevelName(level),
        "service": _service_name,
        "correlationId": get_correlation_id(),
        "event": event,
        **fields,
    }
    logging.getLogger(_LOGGER_NAME).log(level, json.dumps(record, ensure_ascii=False))
