"""Emissão de JWT no login (REQ 03 - ADR-005).

Os claims seguem o contrato que o TokenVerifier (app/security/auth.py, também
copiado no evidence-service) espera: sub, nome, email, role, oab, exp.
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

import jwt


class ITokenIssuer(ABC):
    @abstractmethod
    def issue(
        self, user_id: str, nome: str, email: str, role: str, oab: Optional[str]
    ) -> str: ...

    @abstractmethod
    def expiration_of(self, token: str) -> datetime:
        """Data de expiração (UTC, sem fuso) de um token já validado."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class JwtTokenIssuer(ITokenIssuer):
    def __init__(
        self,
        secret: str,
        algorithm: str,
        expires_in_minutes: int = 60,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._ttl = timedelta(minutes=expires_in_minutes)
        self._clock = clock

    def issue(self, user_id, nome, email, role, oab) -> str:
        now = self._clock()
        claims = {
            "sub": user_id,
            "nome": nome,
            "email": email,
            "role": role,
            "oab": oab,
            "iat": int(now.timestamp()),
            "exp": int((now + self._ttl).timestamp()),
        }
        return jwt.encode(claims, self._secret, algorithm=self._algorithm)

    def expiration_of(self, token: str) -> datetime:
        # O token já passou pelo TokenVerifier; aqui só lemos o `exp`.
        claims = jwt.decode(
            token,
            self._secret,
            algorithms=[self._algorithm],
            options={"require": ["exp"], "verify_exp": False},
        )
        # A coluna revoked_tokens.expires_at é TIMESTAMP sem fuso: guardamos em UTC.
        return datetime.fromtimestamp(claims["exp"], tz=timezone.utc).replace(tzinfo=None)
