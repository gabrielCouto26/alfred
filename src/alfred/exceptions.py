"""Exceções específicas do Alfred."""


class ConfigurationError(RuntimeError):
    """Erro de configuração."""
    pass


class LLMError(RuntimeError):
    """Erro de chamada LLM."""
    pass


class RoutingError(RuntimeError):
    """Erro de roteamento de intenção."""
    pass
