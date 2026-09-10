"""Roteador determinístico de intención basado en heurísticas.

Usado en modo offline/test (``ALFRED_ROUTER=heuristic``) para validar el
flujo E2E de la CLI sin depender del LLM, y como baseline de acurácia sobre
el dataset de evaluación. Mantiene el mismo contrato de salida que el router
LLM (``IntentDecision``).
"""

from typing import Optional

from alfred.contracts import IntentRouter
from alfred.models import (
    AssistantRequest,
    IntentCategory,
    IntentDecision,
    SessionContext,
)


class HeuristicIntentRouter(IntentRouter):
    """Roteador determinístico que clasifica por palabras clave."""

    _blocked_keywords = (
        "rm -rf",
        "drop table",
        "delete database",
        "chmod 777",
        "mkfs",
        "dd if=",
        "password",
        "senha",
        "chave api",
    )

    _out_of_scope_keywords = (
        "whatsapp",
        "webhook",
        "telegram",
        "servidor http",
    )

    _cloud_keywords = (
        "email",
        "inbox",
        "agenda",
        "google",
        "drive",
        "bitcoin",
        "tradu",
        "portugu",
        "reuni",
        "preço",
        "precio",
        "calend",
        "nube",
        "nuvem",
        "cloud",
        "servidor",
    )

    _local_keywords = (
        "archivo",
        "archivos",
        "pasta",
        "directorio",
        "script",
        "terminal",
        "backup",
        "ejecut",
        "execut",
        "comando",
        "limpieza",
        "limpiar",
        "lista",
        "listar",
        "local",
    )

    _chitchat_keywords = (
        "olá",
        "hola",
        "bom dia",
        "buenos días",
        "como vai",
        "como estás",
        "tudo bem",
        "quem é você",
        "quién eres",
        "o que você é",
        "o que você pode",
        "qué puedes hacer",
        "funciona",
        "o que é a vida",
        "qué es la vida",
        "opa",
        "gracias",
        "obrigado",
    )

    _ambiguous_clarification = (
        "Pode ser mais específico? O que você deseja fazer?"
    )

    def classify(
        self,
        request: AssistantRequest,
        context: Optional[SessionContext] = None,
    ) -> IntentDecision:
        """Classificar intenção determinísticamente."""
        message_lower = request.message.lower()

        for keyword in self._blocked_keywords:
            if keyword in message_lower:
                return IntentDecision(
                    category=IntentCategory.BLOCKED,
                    confidence=0.98,
                    rationale_code="blocked_keyword",
                    risk_labels=["blocked"],
                )

        for keyword in self._out_of_scope_keywords:
            if keyword in message_lower:
                return IntentDecision(
                    category=IntentCategory.OUT_OF_SCOPE,
                    confidence=0.95,
                    rationale_code="out_of_scope_keyword",
                )

        for keyword in self._cloud_keywords:
            if keyword in message_lower:
                return IntentDecision(
                    category=IntentCategory.CLOUD_TASK,
                    confidence=0.9,
                    rationale_code="cloud_keyword",
                    simulated_tool_name="cloud_service",
                )

        for keyword in self._local_keywords:
            if keyword in message_lower:
                return IntentDecision(
                    category=IntentCategory.LOCAL_TASK,
                    confidence=0.9,
                    rationale_code="local_keyword",
                    simulated_tool_name="local_task",
                )

        for keyword in self._chitchat_keywords:
            if keyword in message_lower:
                return IntentDecision(
                    category=IntentCategory.CHITCHAT,
                    confidence=0.85,
                    rationale_code="chitchat_keyword",
                )

        return IntentDecision(
            category=IntentCategory.AMBIGUOUS,
            confidence=0.5,
            rationale_code="insufficient_context",
            required_clarification=self._ambiguous_clarification,
        )
