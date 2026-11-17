"""Erros de domínio da recuperação de senha (independentes de HTTP)."""


class WeakPasswordError(ValueError):
    """A nova senha não atende à política (8+ chars, letras, números, símbolos)."""


class InvalidResetTokenError(ValueError):
    """Token de recuperação inexistente, expirado ou já utilizado."""


class MessagePublishError(RuntimeError):
    """Falha ao publicar uma mensagem no broker."""
