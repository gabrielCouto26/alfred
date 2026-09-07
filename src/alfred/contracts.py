"""Contratos e interfaces internas do Alfred."""

from typing_extensions import Protocol


class AssistantService(Protocol):
    """Serviço principal de assistente."""

    def handle(self, request: "AssistantRequest") -> "AssistantResponse":
        """Processar uma solicitação e retornar resposta."""
        ...


class IntentRouter(Protocol):
    """Roteador de classificação de intenção."""

    def classify(
        self, request: "AssistantRequest", context: "SessionContext"
    ) -> "IntentDecision":
        """Classificar intenção da solicitação."""
        ...


class SessionStore(Protocol):
    """Armazenamento de contexto de sessão."""

    def load(self, session_id: str) -> "SessionContext":
        """Carregar contexto de sessão."""
        ...

    def append(self, session_id: str, turn: "SessionTurn") -> None:
        """Adicionar turno à sessão."""
        ...

    def prune_expired(self) -> None:
        """Remover sessões expiradas."""
        ...


class SafetyPolicy(Protocol):
    """Política de segurança para decisões."""

    def evaluate(
        self, decision: "IntentDecision", request: "AssistantRequest"
    ) -> "SafetyDecision":
        """Avaliar decisão e aplicar política de segurança."""
        ...
