"""Cliente OpenRouter com LangChain para chamadas LLM."""

import os
from typing import Optional

from langchain_core.messages import BaseMessage
from langchain_openrouter import ChatOpenRouter
from pydantic import BaseModel

from alfred.config import get_settings
from alfred.exceptions import ConfigurationError, LLMError


class LLMClient:
    """Cliente LLM usando OpenRouter via LangChain."""

    def __init__(self, model: Optional[str] = None):
        """Inicializar cliente com configuração."""
        settings = get_settings()

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ConfigurationError(
                "OPENROUTER_API_KEY não configurada. "
                "Configure a variável de ambiente antes de continuar."
            )

        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini-2024-07-18")
        self.langsmith_tracing = settings.langsmith_tracing
        self.langsmith_api_key = settings.langsmith_api_key

        if self.langsmith_tracing and self.langsmith_api_key:
            os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
            os.environ["LANGSMITH_TRACING"] = "true"

        self.client = ChatOpenRouter(
            model_name=self.model,
            openrouter_api_key=api_key,
            temperature=0.1,
        )

    def generate(
        self,
        messages: list[BaseMessage],
        response_format: Optional[type[BaseModel]] = None,
    ) -> BaseMessage:
        """Gerar resposta do LLM."""
        try:
            if response_format:
                llm_with_output = self.client.with_structured_output(response_format)
            else:
                llm_with_output = self.client

            result = llm_with_output.invoke(messages)

            if response_format and not isinstance(result, response_format):
                raise ValueError(
                    f"Resposta não é do tipo esperado {response_format.__name__}"
                )

            return result
        except Exception as exc:
            raise LLMError(f"Falha na chamada LLM: {exc}") from exc

    def generate_text(self, messages: list[BaseMessage]) -> str:
        """Gerar resposta de texto simples."""
        response = self.generate(messages)
        return response.content if hasattr(response, "content") else str(response)


def create_llm_client(model: Optional[str] = None) -> LLMClient:
    """Factory para criar instância de LLMClient."""
    return LLMClient(model=model)
