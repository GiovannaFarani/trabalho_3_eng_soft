"""AuthService - regras de negócio de Cadastro, Login e Logout (REQ 01, 03, 04).

SRP (Single Responsibility Principle) - ponto a mostrar ao professor
(Pessoa 1). O fluxo de autenticação foi dividido em 3 camadas, cada uma com
UM motivo para mudar:

  - AuthController  (app/routers/auth_router.py)
        só HTTP: lê o corpo, chama o service, converte erro em status code;
  - AuthService     (este arquivo)
        só REGRAS: termos LGPD, senha forte, Decisão D1 (OAB), credenciais,
        emissão/revogação do JWT;
  - UserRepository  (app/repositories/user_repository.py)
        só SQL na tabela `users`.

Se a regra da OAB mudar, só este arquivo muda. Se trocarmos o PostgreSQL, só o
repository muda. Se a API mudar de rota/status, só o controller muda.

Este módulo não importa FastAPI, psycopg2 nem bcrypt (verificado em
tests/test_architecture.py): tudo chega pelo construtor.
"""
import logging
import re
from dataclasses import dataclass
from typing import Callable, ContextManager, Optional

from app.domain.errors import (
    CpfAlreadyRegisteredError,
    EmailAlreadyRegisteredError,
    InvalidCpfError,
    InvalidCredentialsError,
    MissingOabError,
    TermsNotAcceptedError,
    WeakPasswordError,
)
from app.domain.password_policy import PASSWORD_RULE_MESSAGE, is_strong_password
from app.logging_config import log_event
from app.repositories.revoked_token_repository import IRevokedTokenRepository
from app.repositories.user_repository import IUserRepository, NewUser, User
from app.security.jwt_issuer import ITokenIssuer
from app.security.password_hasher import IPasswordHasher

ADVOGADO = "ADVOGADO"
USUARIO_COMUM = "USUARIO_COMUM"
PERFIS = (ADVOGADO, USUARIO_COMUM)

TERMS_MESSAGE = "É obrigatório aceitar os Termos de Uso e Política de Privacidade"
OAB_MESSAGE = "O número da OAB é obrigatório para o perfil Advogado."
CPF_MESSAGE = "CPF inválido: informe os 11 dígitos."
CREDENTIALS_MESSAGE = "E-mail ou senha inválidos."

# Hash bcrypt válido de uma senha qualquer: usado quando o e-mail não existe,
# para o login levar o mesmo tempo nos dois casos e não revelar quais e-mails
# estão cadastrados (enumeração de usuários por tempo de resposta).
_DUMMY_HASH = "$2b$12$ppgGXFOhS0vFvFUODRkezellDurYk9s89SXUugSxFQQSNv8wZU62e"


@dataclass(frozen=True)
class RegisterCommand:
    nome_completo: str
    email: str
    senha: str
    cpf: str
    tipo_perfil: str
    numero_oab: Optional[str]
    termos_aceitos: bool


@dataclass(frozen=True)
class LoginResult:
    token: str
    user: User


def _normalize_cpf(cpf: str) -> str:
    digits = re.sub(r"\D", "", cpf or "")
    if len(digits) != 11:
        raise InvalidCpfError(CPF_MESSAGE)
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


class AuthService:
    def __init__(
        self,
        users: IUserRepository,
        revoked_tokens: IRevokedTokenRepository,
        hasher: IPasswordHasher,
        tokens: ITokenIssuer,
        transaction: Callable[[], ContextManager],
    ) -> None:
        self._users = users
        self._revoked = revoked_tokens
        self._hasher = hasher
        self._tokens = tokens
        self._transaction = transaction

    # ------------------------------------------------------------ REQ 01
    def register(self, cmd: RegisterCommand) -> User:
        # Validação 1 - Termos LGPD
        if cmd.termos_aceitos is not True:
            raise TermsNotAcceptedError(TERMS_MESSAGE)
        # Validação 2 - Senha forte (mesma regra da Tela 1 e do REQ 02)
        if not is_strong_password(cmd.senha):
            raise WeakPasswordError(PASSWORD_RULE_MESSAGE)
        # Validação 3 - Decisão D1: OAB obrigatória só para Advogado
        if cmd.tipo_perfil not in PERFIS:
            raise ValueError(f"tipo_perfil deve ser um de {PERFIS}")
        oab = (cmd.numero_oab or "").strip()
        if cmd.tipo_perfil == ADVOGADO and not oab:
            raise MissingOabError(OAB_MESSAGE)
        numero_oab = oab if cmd.tipo_perfil == ADVOGADO else None  # Usuário Comum: força NULL

        new_user = NewUser(
            nome_completo=cmd.nome_completo.strip(),
            email=cmd.email.strip().lower(),
            senha_hash=self._hasher.hash(cmd.senha),
            cpf=_normalize_cpf(cmd.cpf),
            tipo_perfil=cmd.tipo_perfil,
            numero_oab=numero_oab,
            termos_aceitos=True,
        )
        try:
            with self._transaction() as cur:
                user = self._users.create(cur, new_user)
        except EmailAlreadyRegisteredError:
            log_event(logging.INFO, "user_register_duplicate_email")
            raise
        except CpfAlreadyRegisteredError:
            log_event(logging.INFO, "user_register_duplicate_cpf")
            raise
        log_event(logging.INFO, "user_registered", userId=user.id, role=user.tipo_perfil)
        return user

    # ------------------------------------------------------------ REQ 03
    def login(self, email: str, senha: str) -> LoginResult:
        with self._transaction() as cur:
            user = self._users.find_by_email(cur, email.strip())
        password_ok = self._hasher.verify(senha, user.senha_hash if user else _DUMMY_HASH)
        if user is None or not password_ok:
            log_event(logging.INFO, "user_login_failed")
            raise InvalidCredentialsError(CREDENTIALS_MESSAGE)
        token = self._tokens.issue(
            user_id=user.id,
            nome=user.nome_completo,
            email=user.email,
            role=user.tipo_perfil,
            oab=user.numero_oab,
        )
        log_event(logging.INFO, "user_logged_in", userId=user.id, role=user.tipo_perfil)
        return LoginResult(token=token, user=user)

    # ------------------------------------------------------------ REQ 04
    def logout(self, token: str, user_id: str) -> None:
        """Revoga o token (já validado pelo TokenVerifier) até ele expirar."""
        expires_at = self._tokens.expiration_of(token)
        with self._transaction() as cur:
            self._revoked.revoke(cur, token, expires_at)
        log_event(logging.INFO, "user_logged_out", userId=user_id)
