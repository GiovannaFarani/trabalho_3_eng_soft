import os

os.environ.setdefault("DATABASE_URL", "postgresql://u:p@localhost:5432/x")
os.environ.setdefault("JWT_SECRET", "segredo-de-teste-com-mais-de-32-caracteres!!")
