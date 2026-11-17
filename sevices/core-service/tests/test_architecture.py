"""Fitness functions (ADR-014): checagens automáticas de arquitetura."""
import ast
import pathlib

APP = pathlib.Path(__file__).resolve().parent.parent / "app"


def _imports(path: pathlib.Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield a.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


def test_service_layer_does_not_depend_on_infrastructure_dip():
    forbidden = {"pika", "psycopg2", "bcrypt", "fastapi"}
    for f in (APP / "services").glob("*.py"):
        roots = {m.split(".")[0] for m in _imports(f)}
        assert not (roots & forbidden), f"{f.name} importa infraestrutura: {roots & forbidden}"


def test_only_rabbitmq_publisher_knows_pika():
    for f in APP.rglob("*.py"):
        roots = {m.split(".")[0] for m in _imports(f)}
        if f.name != "rabbitmq_publisher.py":
            assert "pika" not in roots, f"{f} não deveria importar pika"


def test_core_service_does_not_import_evidence_service():
    for f in APP.rglob("*.py"):
        for module in _imports(f):
            assert "evidence" not in module, f"{f.name} importa código do evidence-service: {module}"
