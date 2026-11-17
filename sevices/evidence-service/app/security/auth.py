"""Autenticação JWT + Blacklist + RBAC (ADR-005 e ADR-010).

Fluxo de `get_current_user` (dependência FastAPI):
  1. exige header `Authorization: Bearer <token>`;
  2. valida assinatura e expiração do JWT (algoritmo fixo, nunca o do token);
  3. consulta a blacklist -> 401 "Sessão encerrada. Faça login novamente";
  4. devolve AuthenticatedUser (id vem do `sub` do token).

ISOLAMENTO DE TENANT (ADR-010): os serviços devem usar SEMPRE `user.id` vindo
daqui para filtrar dados (ex.: WHERE user_id = user.id) e NUNCA um userId
recebido pela URL/query/body.

RBAC: `require_roles("ADVOGADO")` devolve uma dependência que responde 403 se
o papel do token não estiver na lista.

ESTE ARQUIVO É COPIADO para evidence-service/app/security/ (o roteiro manda
copiar; assim nenhum serviço importa código interno do outro - ADR-014).
"""
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
    """Valida um JWT (regra de negócio), sem saber nada de HTTP."""

    def __init__(self, secret: str, algorithm: str, blacklist: ITokenBlacklist) -> None:
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
            raise AuthenticationError("Token expirado. Faça login novamente.") from exc
        except jwt.InvalidTokenError as exc:
            raise AuthenticationError("Token inválido.") from exc

        if self._blacklist.is_revoked(token):
            raise AuthenticationError("Sessão encerrada. Faça login novamente")

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


def get_token_verifier() -> TokenVerifier:  # pragma: no cover - sobrescrita por app.dependencies
    raise NotImplementedError("Registre o provider em app.dependencies")


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
            status.HTTP_401_UNAUTHORIZED, str(exc), headers=_UNAUTHENTICATED
        ) from exc


def require_roles(*allowed_roles: str) -> Callable[..., AuthenticatedUser]:
    """RBAC: permite apenas os papéis informados (ex.: 'ADVOGADO', 'USUARIO_COMUM')."""

    def dependency(user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "Você não tem permissão para acessar este recurso."
            )
        return user

    return dependency
