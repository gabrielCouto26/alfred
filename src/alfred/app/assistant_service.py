"""Serviço principal de assistente."""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from alfred import observability
from alfred.contracts import AssistantService, IntentRouter, SafetyPolicy, SessionStore
from alfred.models import (
    AssistantRequest,
    AssistantResponse,
    CloudTaskIntent,
    IntentCategory,
    IntentDecision,
    LocalTaskIntent,
    SafetyDecision,
    SafetyStatus,
    SessionTurn,
    SimulatedToolResponse,
)

if TYPE_CHECKING:
    from alfred.tools.simulated_registry import SimulatedToolsRegistry


class AssistantServiceImpl(AssistantService):
    """Implementação do serviço principal de assistente."""

    def __init__(
        self,
        intent_router: IntentRouter,
        safety_policy: SafetyPolicy,
        session_store: SessionStore,
        simulated_tools_registry: "SimulatedToolsRegistry",
    ):
        """Inicializar serviço com dependências."""
        self._intent_router = intent_router
        self._safety_policy = safety_policy
        self._session_store = session_store
        self._simulated_tools_registry = simulated_tools_registry

    def handle(self, request: AssistantRequest) -> AssistantResponse:
        """Processar uma solicitação e retornar resposta."""
        trace_id = ""
        telemetry = observability.get_telemetry_client()
        start_time = datetime.now()

        try:
            session_id = request.session_id
            context = self._session_store.load(session_id)

            if request.trace_enabled:
                trace_id = telemetry.generate_trace_id()
                telemetry.emit_request(session_id, trace_id)

            intent_decision = self._intent_router.classify(request, context)
            safety_decision = self._safety_policy.evaluate(intent_decision, request)

            if request.trace_enabled and intent_decision:
                latency_ms = (datetime.now() - start_time).total_seconds() * 1000
                telemetry.emit_classification(
                    session_id=session_id,
                    category=intent_decision.category.value,
                    confidence=intent_decision.confidence,
                    rationale_code=intent_decision.rationale_code,
                    trace_id=trace_id,
                    latency_ms=latency_ms,
                )
                telemetry.emit_safety_check(
                    session_id=session_id,
                    category=intent_decision.category.value,
                    safety_status=safety_decision.status.value,
                    decision_hash=intent_decision.decision_hash,
                    trace_id=trace_id,
                )

            if safety_decision.status == SafetyStatus.BLOCK:
                if request.trace_enabled:
                    telemetry.emit_response(
                        session_id=session_id,
                        category=intent_decision.category.value,
                        safety_status=safety_decision.status.value,
                        decision_hash=intent_decision.decision_hash,
                        trace_id=trace_id,
                    )
                return self._build_blocked_response(
                    request, intent_decision, safety_decision
                )

            if safety_decision.status == SafetyStatus.CONFIRM:
                if not request.interactive_confirmation:
                    if request.trace_enabled:
                        telemetry.emit_response(
                            session_id=session_id,
                            category=intent_decision.category.value,
                            safety_status=safety_decision.status.value,
                            decision_hash=intent_decision.decision_hash,
                            trace_id=trace_id,
                        )
                    return self._build_blocked_response(
                        request, intent_decision, safety_decision
                    )
                confirmed = self._prompt_confirmation(safety_decision.human_message)
                if not confirmed:
                    if request.trace_enabled:
                        telemetry.emit_response(
                            session_id=session_id,
                            category=intent_decision.category.value,
                            safety_status=safety_decision.status.value,
                            decision_hash=intent_decision.decision_hash,
                            trace_id=trace_id,
                        )
                    return self._build_blocked_response(
                        request, intent_decision, safety_decision
                    )

            if intent_decision.category == IntentCategory.CHITCHAT:
                text = self._generate_chitchat_response(intent_decision, request)
                if request.trace_enabled:
                    telemetry.emit_response(
                        session_id=session_id,
                        category=intent_decision.category.value,
                        safety_status=safety_decision.status.value,
                        decision_hash=intent_decision.decision_hash,
                        trace_id=trace_id,
                    )
                return self._build_success_response(
                    request, intent_decision, safety_decision, text
                )

            if intent_decision.category == IntentCategory.AMBIGUOUS:
                if intent_decision.required_clarification:
                    text = intent_decision.required_clarification
                else:
                    text = "Não entendi. Pode ser mais específico?"
                if request.trace_enabled:
                    telemetry.emit_response(
                        session_id=session_id,
                        category=intent_decision.category.value,
                        safety_status=safety_decision.status.value,
                        decision_hash=intent_decision.decision_hash,
                        trace_id=trace_id,
                    )
                return self._build_ambiguous_response(
                    request, intent_decision, safety_decision, text
                )

            if intent_decision.category == IntentCategory.CLOUD_TASK:
                if not intent_decision.simulated_tool_name:
                    if request.trace_enabled:
                        telemetry.emit_response(
                            session_id=session_id,
                            category=intent_decision.category.value,
                            safety_status=safety_decision.status.value,
                            decision_hash=intent_decision.decision_hash,
                            trace_id=trace_id,
                        )
                    return self._build_ambiguous_response(
                        request,
                        intent_decision,
                        safety_decision,
                        "Ferramenta não especificada",
                    )
                task = CloudTaskIntent(task_name=intent_decision.simulated_tool_name)
                tool_response = self._simulated_tools_registry.simulate_cloud_task(task)
                if request.trace_enabled:
                    telemetry.emit_response(
                        session_id=session_id,
                        category=intent_decision.category.value,
                        safety_status=safety_decision.status.value,
                        decision_hash=intent_decision.decision_hash,
                        trace_id=trace_id,
                    )
                return self._build_task_response(
                    request, intent_decision, safety_decision, tool_response
                )

            if intent_decision.category == IntentCategory.LOCAL_TASK:
                if not intent_decision.simulated_tool_name:
                    if request.trace_enabled:
                        telemetry.emit_response(
                            session_id=session_id,
                            category=intent_decision.category.value,
                            safety_status=safety_decision.status.value,
                            decision_hash=intent_decision.decision_hash,
                            trace_id=trace_id,
                        )
                    return self._build_ambiguous_response(
                        request,
                        intent_decision,
                        safety_decision,
                        "Ferramenta não especificada",
                    )
                task = LocalTaskIntent(task_name=intent_decision.simulated_tool_name)
                tool_response = self._simulated_tools_registry.simulate_local_task(task)
                if request.trace_enabled:
                    telemetry.emit_response(
                        session_id=session_id,
                        category=intent_decision.category.value,
                        safety_status=safety_decision.status.value,
                        decision_hash=intent_decision.decision_hash,
                        trace_id=trace_id,
                    )
                return self._build_task_response(
                    request, intent_decision, safety_decision, tool_response
                )

            if intent_decision.category == IntentCategory.OUT_OF_SCOPE:
                text = "Estou fora de escopo neste momento."
                if request.trace_enabled:
                    telemetry.emit_response(
                        session_id=session_id,
                        category=intent_decision.category.value,
                        safety_status=safety_decision.status.value,
                        decision_hash=intent_decision.decision_hash,
                        trace_id=trace_id,
                    )
                return self._build_out_of_scope_response(
                    request, intent_decision, safety_decision, text
                )

            if request.trace_enabled:
                telemetry.emit_response(
                    session_id=session_id,
                    category=intent_decision.category.value,
                    safety_status=safety_decision.status.value,
                    decision_hash=intent_decision.decision_hash,
                    trace_id=trace_id,
                )
            return self._build_error_response(request, "classificação não tratada")

        except Exception as exc:
            if request.trace_enabled:
                telemetry.emit_response(
                    session_id=session_id,
                    category="AMBIGUOUS",
                    safety_status="BLOCK",
                    decision_hash="",
                    trace_id=trace_id,
                )
            return self._build_error_response(request, str(exc))

    def _build_blocked_response(
        self,
        request: AssistantRequest,
        intent_decision: IntentDecision,
        safety_decision: SafetyDecision,
    ) -> AssistantResponse:
        """Construir resposta de bloqueio."""
        self._persist_session(request.session_id, intent_decision, safety_decision)
        return AssistantResponse(
            text=safety_decision.human_message,
            category=intent_decision.category,
            safety_status=SafetyStatus.BLOCK,
            session_id=request.session_id,
            metadata={
                "rationale_code": intent_decision.rationale_code,
                "reason_code": safety_decision.reason_code,
            },
        )

    def _build_success_response(
        self,
        request: AssistantRequest,
        intent_decision: IntentDecision,
        safety_decision: SafetyDecision,
        text: str,
    ) -> AssistantResponse:
        """Construir resposta de sucesso."""
        self._persist_session(request.session_id, intent_decision, safety_decision)
        return AssistantResponse(
            text=text,
            category=intent_decision.category,
            safety_status=safety_decision.status,
            session_id=request.session_id,
            metadata={"rationale_code": intent_decision.rationale_code},
        )

    def _build_ambiguous_response(
        self,
        request: AssistantRequest,
        intent_decision: IntentDecision,
        safety_decision: SafetyDecision,
        text: str,
    ) -> AssistantResponse:
        """Construir resposta de ambiguidade."""
        self._persist_session(request.session_id, intent_decision, safety_decision)
        return AssistantResponse(
            text=text,
            category=intent_decision.category,
            safety_status=safety_decision.status,
            session_id=request.session_id,
            metadata={"rationale_code": intent_decision.rationale_code},
        )

    def _build_task_response(
        self,
        request: AssistantRequest,
        intent_decision: IntentDecision,
        safety_decision: SafetyDecision,
        tool_response: SimulatedToolResponse,
    ) -> AssistantResponse:
        """Construir resposta de tarefa."""
        self._persist_session(request.session_id, intent_decision, safety_decision)
        return AssistantResponse(
            text=tool_response.human_message,
            category=intent_decision.category,
            safety_status=safety_decision.status,
            session_id=request.session_id,
            metadata={
                "rationale_code": intent_decision.rationale_code,
                "tool_status": tool_response.status,
                "tool_intention": tool_response.intention,
                "tool_requires_confirmation": tool_response.requires_confirmation,
            },
        )

    def _build_out_of_scope_response(
        self,
        request: AssistantRequest,
        intent_decision: IntentDecision,
        safety_decision: SafetyDecision,
        text: str,
    ) -> AssistantResponse:
        """Construir resposta de fora de escopo."""
        self._persist_session(request.session_id, intent_decision, safety_decision)
        return AssistantResponse(
            text=text,
            category=intent_decision.category,
            safety_status=safety_decision.status,
            session_id=request.session_id,
            metadata={"rationale_code": intent_decision.rationale_code},
        )

    def _build_error_response(
        self, request: AssistantRequest, error_message: str
    ) -> AssistantResponse:
        """Construir resposta de erro."""
        return AssistantResponse(
            text=f"Erro: {error_message}",
            category=IntentCategory.AMBIGUOUS,
            safety_status=SafetyStatus.BLOCK,
            session_id=request.session_id,
            metadata={"error": error_message},
        )

    def _persist_session(
        self,
        session_id: str,
        intent_decision: IntentDecision,
        safety_decision: SafetyDecision,
    ) -> None:
        """Persistir resumo da sessão (nunca mensagem bruta)."""
        now = datetime.now()
        turn = SessionTurn(
            created_at=now,
            expires_at=now + timedelta(seconds=7200),
            category=intent_decision.category,
            summary=(
                f"[{safety_decision.status.value}] "
                f"{intent_decision.category.value}"
            ),
            decision_hash=intent_decision.decision_hash,
            category_label=intent_decision.category.value,
            risk_labels=intent_decision.risk_labels,
        )
        self._session_store.append(session_id, turn)

    def _prompt_confirmation(self, message: str) -> bool:
        """Solicitar confirmação interativa ao usuário."""
        try:
            response = input(f"{message} (s/N): ")
            return response.lower().strip() in ("s", "sim", "y", "yes")
        except (EOFError, OSError):
            return False

    def _generate_chitchat_response(
        self, intent_decision: IntentDecision, request: AssistantRequest
    ) -> str:
        """Gerar resposta para chitchat."""
        message_lower = request.message.lower()

        if any(w in message_lower for w in ["olá", "oi ", "bom dia"]):
            return "Olá! Como posso ajudar hoje?"
        if any(w in message_lower for w in ["como vai", "tudo bem"]):
            return "Estou bem, pronto para ajudar!"
        if any(w in message_lower for w in ["quem é você", "o que você é"]):
            return "Sou Alfred, seu assistente pessoal."
        return "Interessante. O que você gostaria de fazer?"
