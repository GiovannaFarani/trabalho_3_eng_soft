import json
import logging

from fastapi.testclient import TestClient

from app.logging_config import get_correlation_id, log_event
from app.main import create_app


def _client():
    app = create_app()

    @app.get("/_probe")
    def probe():
        # Código "de negócio" logando: deve herdar o correlationId sem recebê-lo.
        log_event(logging.INFO, "inside_endpoint")
        return {"cid": get_correlation_id()}

    return TestClient(app)


def _json_logs(caplog):
    out = []
    for rec in caplog.records:
        if rec.name == "veridt":
            out.append(json.loads(rec.getMessage()))
    return out


def test_generates_uuid_when_header_missing(caplog):
    caplog.set_level(logging.INFO)
    r = _client().get("/_probe")
    cid = r.headers["X-Correlation-ID"]
    assert len(cid) == 36 and r.json()["cid"] == cid


def test_reuses_incoming_header(caplog):
    caplog.set_level(logging.INFO)
    r = _client().get("/_probe", headers={"X-Correlation-ID": "abc-123"})
    assert r.headers["X-Correlation-ID"] == "abc-123"


def test_rejects_malformed_header_and_generates_new(caplog):
    caplog.set_level(logging.INFO)
    r = _client().get("/_probe", headers={"X-Correlation-ID": "ruim valor com espacos"})
    assert r.headers["X-Correlation-ID"] != "ruim valor com espacos"


def test_access_log_is_structured_json_with_required_fields(caplog):
    caplog.set_level(logging.INFO)
    _client().get("/_probe", headers={"X-Correlation-ID": "log-1"})
    logs = _json_logs(caplog)
    access = next(l for l in logs if l["event"] == "http_request")
    assert access["service"] == "core-service"
    assert access["correlationId"] == "log-1"
    assert access["method"] == "GET" and access["path"] == "/_probe" and access["statusCode"] == 200
    assert "timestamp" in access
    inner = next(l for l in logs if l["event"] == "inside_endpoint")
    assert inner["correlationId"] == "log-1"


def test_status_code_is_logged_for_errors(caplog):
    caplog.set_level(logging.INFO)
    _client().get("/nao-existe", headers={"X-Correlation-ID": "e-404"})
    access = next(l for l in _json_logs(caplog) if l["event"] == "http_request")
    assert access["statusCode"] == 404
