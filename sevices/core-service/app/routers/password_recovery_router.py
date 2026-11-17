"""Controller HTTP da recuperação de senha (REQ 02, parte 1).

Só traduz HTTP <-> service: valida o corpo (Pydantic), chama o service e mapeia
erros de domínio em status codes. Nenhuma regra de negócio aqui.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.errors import InvalidResetTokenError, WeakPasswordError
from app.logging_config import get_correlation_id
from app.schemas import ForgotPasswordRequest, MessageResponse, ResetPasswordRequest
from app.services.password_recovery_service import PasswordRecoveryService
from app.dependencies import get_password_recovery_service

router = APIRouter(prefix="/api/auth", tags=["Recuperação de senha (REQ 02)"])


@router.post("/forgot-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def forgot_password(
    body: ForgotPasswordRequest,
    service: PasswordRecoveryService = Depends(get_password_recovery_service),
) -> MessageResponse:
    service.request_reset(body.email, correlation_id=get_correlation_id())
    # Sempre 200: não revela se o e-mail está ou não cadastrado.
    return MessageResponse(
        message="Se o e-mail informado estiver cadastrado, as instruções de recuperação foram enviadas."
    )


@router.post("/reset-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def reset_password(
    body: ResetPasswordRequest,
    service: PasswordRecoveryService = Depends(get_password_recovery_service),
) -> MessageResponse:
    try:
        service.reset_password(body.token, body.nova_senha)
    except WeakPasswordError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    except InvalidResetTokenError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    return MessageResponse(message="Senha redefinida com sucesso.")
