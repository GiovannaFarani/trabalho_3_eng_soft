"""Alerta de divergência: os arquivos copiados para o evidence-service devem ser
idênticos aos originais do core-service (o roteiro manda COPIAR o middleware)."""
import pathlib

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SHARED = [
    "logging_config.py", "db.py",
    "middleware/correlation_id.py", "security/auth.py", "security/token_blacklist.py",
]


@pytest.mark.skipif(not (ROOT / "evidence-service").exists(), reason="evidence-service ausente")
@pytest.mark.parametrize("rel", SHARED)
def test_copy_is_identical(rel):
    core = (ROOT / "core-service/app" / rel).read_text(encoding="utf-8")
    evidence = (ROOT / "evidence-service/app" / rel).read_text(encoding="utf-8")
    assert core == evidence, f"{rel} divergiu entre os serviços; recopie do core-service"
