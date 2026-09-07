"""Exceções customizadas do Alfred."""


class AlfredError(Exception):
    """Erro base do Alfred."""
    
    pass


class ConfigurationError(AlfredError):
    """Erro de configuração."""
    
    pass


class InputError(AlfredError):
    """Erro de entrada inválida."""
    
    pass


class ToolError(AlfredError):
    """Erro de execução de tool."""
    
    pass
