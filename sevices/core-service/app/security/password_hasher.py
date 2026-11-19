"""Hash de senha com bcrypt (REQ 01 / REQ 03).

O AuthService depende de IPasswordHasher, não do bcrypt (DIP): nos testes
usamos um hasher falso e rápido.
"""
from abc import ABC, abstractmethod

import bcrypt

# bcrypt só considera os primeiros 72 bytes; a versão 5 do pacote levanta erro
# acima disso. Truncamos explicitamente para hash e verificação ficarem iguais.
_BCRYPT_MAX_BYTES = 72


def _encode(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


class IPasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...

    @abstractmethod
    def verify(self, password: str, password_hash: str) -> bool: ...


class BcryptPasswordHasher(IPasswordHasher):
    def __init__(self, rounds: int = 12) -> None:
        self._rounds = rounds

    def hash(self, password: str) -> str:
        return bcrypt.hashpw(_encode(password), bcrypt.gensalt(self._rounds)).decode("utf-8")

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(_encode(password), password_hash.encode("utf-8"))
        except ValueError:
            # Hash malformado no banco: trata como senha errada, sem derrubar o login.
            return False
