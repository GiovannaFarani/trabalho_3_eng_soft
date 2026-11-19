
from dataclasses import dataclass
from typing import Callable, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.security.token_blacklist import ITokenBlacklist


_bearer = HTTPBearer(auto_error=False)
_UNAUTHENTICATED = {"WWW-Authenticate": "Bearer"}


@dataclass(frozen=True)
class AuthenticatedUser:
    id: str
    nome: Optional[str]
    email: Optional[str]
    role: str
    oab: Optional[str]


class AuthenticationError(Exception):
    """Token ausente, inválido, expirado ou revogado."""


class TokenVerifier:

    def __init__(
        self,
        secret: str,
        algorithm: str,
        blacklist: ITokenBlacklist
    ) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._blacklist = blacklist

    def verify(self, token: str) -> AuthenticatedUser:
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=[self._algorithm],
                options={"require": ["exp", "sub"]},
            )

        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationError(
                "Token expirado. Faça login novamente."
            ) from exc

        except jwt.InvalidTokenError as exc:
            raise AuthenticationError("Token inválido.") from exc

        if self._blacklist.is_revoked(token):
            raise AuthenticationError(
                "Sessão encerrada. Faça login novamente"
            )

        role = claims.get("role")

        if not role:
            raise AuthenticationError("Token inválido.")

        return AuthenticatedUser(
            id=str(claims["sub"]),
            nome=claims.get("nome"),
            email=claims.get("email"),
            role=role,
            oab=claims.get("oab"),
        )


def get_token_verifier() -> TokenVerifier:
    raise NotImplementedError(
        "Registre o provider em app.dependencies"
    )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    verifier: TokenVerifier = Depends(get_token_verifier),
) -> AuthenticatedUser:

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Autenticação necessária.",
            headers=_UNAUTHENTICATED,
        )

    try:
        return verifier.verify(credentials.credentials)

    except AuthenticationError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            str(exc),
            headers=_UNAUTHENTICATED
        ) from exc


def require_roles(*allowed_roles: str) -> Callable[..., AuthenticatedUser]:

    def dependency(
        user: AuthenticatedUser = Depends(get_current_user)
    ) -> AuthenticatedUser:

        if user.role not in allowed_roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "Você não tem permissão para acessar este recurso."
            )

        return user

    return dependency
