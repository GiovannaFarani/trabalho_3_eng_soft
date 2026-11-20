"""Erros de domínio do core-service (independentes de HTTP)."""


class WeakPasswordError(ValueError):
    """A nova senha não atende à política (8+ chars, letras, números, símbolos)."""


class InvalidResetTokenError(ValueError):
    """Token de recuperação inexistente, expirado ou já utilizado."""


class MessagePublishError(RuntimeError):
    """Falha ao publicar uma mensagem no broker."""


# ---------------------------------------------------------------- REQ 01/03/04
class TermsNotAcceptedError(ValueError):
    """Cadastro sem aceite dos Termos de Uso e Política de Privacidade (LGPD)."""


class MissingOabError(ValueError):
    """Perfil ADVOGADO sem número da OAB (Decisão D1)."""


class InvalidCpfError(ValueError):
    """CPF não tem 11 dígitos."""


class EmailAlreadyRegisteredError(ValueError):
    """Já existe usuário com este e-mail."""


class CpfAlreadyRegisteredError(ValueError):
    """Já existe usuário com este CPF."""


class InvalidCredentialsError(ValueError):
    """E-mail ou senha incorretos no login."""
