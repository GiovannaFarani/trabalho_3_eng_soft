"""AuthController - Cadastro, Login e Logout (REQ 01, REQ 03, REQ 04).

Camada HTTP do SRP (ver app/services/auth_service.py): só traduz
requisição -> comando do service e erro de domínio -> status code.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies import get_auth_service
from app.domain.errors import (
    CpfAlreadyRegisteredError,
    EmailAlreadyRegisteredError,
    InvalidCpfError,
    InvalidCredentialsError,
    MissingOabError,
    TermsNotAcceptedError,
    WeakPasswordError,
)
from app.schemas import (
    LoginRequest,
    LoginResponse,
    MessageResponse,
    RegisterRequest,
    UserResponse,
)
from app.security.auth import AuthenticatedUser, get_current_user
from app.services.auth_service import AuthService, RegisterCommand

router = APIRouter(prefix="/api/auth", tags=["Autenticação (REQ 01, 03, 04)"])

# get_current_user já valida o token; este HTTPBearer só entrega o texto do
# token ao logout (o FastAPI reaproveita o mesmo header).
_bearer = HTTPBearer(auto_error=False)


def _to_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        nome_completo=user.nome_completo,
        email=user.email,
        cpf=user.cpf,
        tipo_perfil=user.tipo_perfil,
        numero_oab=user.numero_oab,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    body: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    try:
        user = service.register(RegisterCommand(**body.model_dump()))
    except (TermsNotAcceptedError, WeakPasswordError, MissingOabError, InvalidCpfError) as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except (EmailAlreadyRegisteredError, CpfAlreadyRegisteredError) as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    return _to_response(user)


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> LoginResponse:
    try:
        result = service.login(body.email, body.senha)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, str(exc), headers={"WWW-Authenticate": "Bearer"}
        ) from exc
    return LoginResponse(token=result.token, user=_to_response(result.user))


@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def logout(
    user: AuthenticatedUser = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    # Se chegou aqui, get_current_user já garantiu: token presente, assinatura
    # válida, não expirado e não revogado (senão seria 401).
    service.logout(credentials.credentials, user.id)
    return MessageResponse(message="Logout realizado e token revogado")
