"""Roteador de classificação de intenção com LLM."""

from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage

from alfred.contracts import IntentRouter
from alfred.llm.openrouter_client import create_llm_client
from alfred.models import (
    AssistantRequest,
    IntentCategory,
    IntentDecision,
    SessionContext,
)
from alfred.routing.prompts import INTENT_CLASSIFICATION_PROMPT


class IntentRouterImpl(IntentRouter):
    """Roteador de classificação de intenção com output estruturado."""

    def __init__(self, model: Optional[str] = None):
        """Inicializar roteador com cliente LLM."""
        self.llm_client = create_llm_client(model=model)

    def classify(
        self, request: AssistantRequest, context: Optional[SessionContext] = None
    ) -> IntentDecision:
        """Classificar intenção da solicitação."""
        history = self._build_history(context, request)
        prompt = INTENT_CLASSIFICATION_PROMPT.format(
            message=request.message,
            channel=request.channel.value,
            history=history,
        )

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Avaliar: {request.message}"),
        ]

        response = self.llm_client.generate(
            messages,
            response_format=IntentDecision,
        )

        if not isinstance(response, IntentDecision):
            raise ValueError("Resposta LLM não é um IntentDecision válido")

        decision = self._post_process_decision(response, request)
        return decision

    def _build_history(
        self, context: Optional[SessionContext], request: AssistantRequest
    ) -> str:
        """Construir histórico da sessão."""
        if not context or not context.turns:
            return ""

        recent_turns = context.turns[-3:]
        history_lines = [
            f"- [{t.category.value}] {t.summary}" for t in recent_turns
        ]
        return "\n".join(history_lines)

    def _post_process_decision(
        self, decision: IntentDecision, request: AssistantRequest
    ) -> IntentDecision:
        """Pós-processar decisão após saída do LLM."""
        decision.rationale_code = self._generate_rationale_code(decision, request)
        return decision

    def _generate_rationale_code(
        self, decision: IntentDecision, request: AssistantRequest
    ) -> str:
        """Gerar código de justificativa baseado em heurísticas."""
        message_lower = request.message.lower()

        if decision.category == IntentCategory.CHITCHAT:
            if any(w in message_lower for w in ["olá", "oi ", "bom dia", "boa noite"]):
                return "greeting_detected"
            if any(w in message_lower for w in ["como vai", "tudo bem", "怎么样"]):
                return "wellness_check"
            if any(w in message_lower for w in ["quem é você", "o que você é"]):
                return "identity_question"
            return "chitchat_pattern"

        if decision.category == IntentCategory.CLOUD_TASK:
            if any(w in message_lower for w in ["nuvem", "cloud", "servidor", "web"]):
                return "cloud_keyword"
            if any(w in message_lower for w in ["email", "gmail", "calendar", "agenda"]):
                return "cloud_service"
            if any(w in message_lower for w in ["arquivo", "drive", "google drive"]):
                return "cloud_storage"
            return "cloud_task_pattern"

        if decision.category == IntentCategory.LOCAL_TASK:
            if any(w in message_lower for w in ["local", "arquivo", "script", "terminal"]):
                return "local_keyword"
            if any(w in message_lower for w in ["execute", "run", "rodar", "comando"]):
                return "local_execution"
            if any(w in message_lower for w in ["arquivos", "pasta", "diretório"]):
                return "local_files"
            return "local_task_pattern"

        if decision.category == IntentCategory.AMBIGUOUS:
            if "?" in request.message:
                return "question_mark"
            if len(request.message.split()) < 3:
                return "insufficient_context"
            return "ambiguous_pattern"

        if decision.category == IntentCategory.BLOCKED:
            return "blocked_pattern"

        if decision.category == IntentCategory.OUT_OF_SCOPE:
            return "out_of_scope_pattern"

        return "default_classification"


def create_intent_router(model: Optional[str] = None) -> IntentRouter:
    """Factory para criar instância de IntentRouter."""
    return IntentRouterImpl(model=model)
