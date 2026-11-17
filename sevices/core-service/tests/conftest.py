import os

# Variáveis mínimas ANTES de qualquer import de app.* (Settings é lida de env).
os.environ.setdefault("DATABASE_URL", "postgresql://u:p@localhost:5432/x")
os.environ.setdefault("JWT_SECRET", "segredo-de-teste-com-mais-de-32-caracteres!!")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
