"""Middleware de Correlation ID + log de acesso estruturado (ADR-009).

Para cada requisição HTTP:
  1. lê o header X-Correlation-ID; se ausente ou malformado, gera um UUID4;
  2. guarda o ID numa ContextVar (visível em todo o código da requisição) e em
     request.state.correlation_id;
  3. devolve o mesmo ID no header X-Correlation-ID da resposta;
  4. ao final, imprime um JSON: timestamp, service, correlationId, method,
     path, statusCode (mais event, level e durationMs).

É um middleware ASGI "puro" (não BaseHTTPMiddleware) para que a ContextVar
propague corretamente para os endpoints síncronos executados em threadpool.
"""
import logging
import re
import time
import uuid

from app.logging_config import correlation_id_var, log_event

HEADER_NAME = "X-Correlation-ID"
# Só aceitamos IDs "seguros": evita injeção de quebras de linha/lixo nos logs.
_VALID_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


class CorrelationIdMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = None
        for name, value in scope.get("headers", []):
            if name == b"x-correlation-id":
                incoming = value.decode("latin-1")
                break
        correlation_id = incoming if incoming and _VALID_ID.match(incoming) else str(uuid.uuid4())

        scope.setdefault("state", {})["correlation_id"] = correlation_id
        token = correlation_id_var.set(correlation_id)
        status_holder = {"code": 500}
        started = time.perf_counter()

        async def send_with_header(message) -> None:
            if message["type"] == "http.response.start":
                status_holder["code"] = message["status"]
                headers = [
                    (k, v) for k, v in message.get("headers", [])
                    if k.lower() != b"x-correlation-id"
                ]
                headers.append((HEADER_NAME.lower().encode(), correlation_id.encode()))
                message = {**message, "headers": headers}
            await send(message)

        try:
            await self.app(scope, receive, send_with_header)
        finally:
            log_event(
                logging.INFO,
                "http_request",
                method=scope.get("method"),
                path=scope.get("path"),
                statusCode=status_holder["code"],
                durationMs=round((time.perf_counter() - started) * 1000, 2),
            )
            correlation_id_var.reset(token)
