"""Configurações do Alfred."""

import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Configurações do Alfred."""
    
    openrouter_api_key: str | None = None
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    session_ttl_seconds: int = 7200
    
    class Config:
        env_prefix = "ALFRED_"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Obter instância única de configurações."""
    return Settings()


def load_openrouter_api_key() -> str:
    """Carregar chave da OpenRouter do ambiente."""
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError(
            "OPENROUTER_API_KEY não configurada. "
            "Configure a variável de ambiente antes de continuar."
        )
    return key
