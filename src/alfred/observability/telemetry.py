"""Camada de observabilidade com logs locais e LangSmith opcional."""

import hashlib
import logging
import os
import secrets
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class TelemetryEvent(BaseModel):
    """Evento de telemetry estruturado."""

    event_type: str = Field(..., description="Tipo do evento")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp")
    session_id: str = Field(..., description="ID da sessão")
    intent_category: str = Field(..., description="Categoria da intenção")
    safety_status: str = Field(..., description="Status de segurança")
    intent_confidence: float | None = Field(
        default=None, description="Confiança da intenção"
    )
    decision_hash: str = Field(..., description="Hash da decisão")
    latency_ms: float | None = Field(default=None, description="Latência em ms")
    llm_model: str | None = Field(default=None, description="Modelo LLM usado")
    trace_id: str = Field(..., description="ID de trace para correlação")
    is_tracing_disabled: bool = Field(
        default=False, description="Se tracing foi desabilitado"
    )


class TelemetryClient:
    """Cliente de telemetry com logs locais e LangSmith opcional."""

    def __init__(self, enabled: bool = True, disable_content_tracing: bool = True):
        self._enabled = enabled
        self._disable_content_tracing = disable_content_tracing
        self._langsmith_tracing = (
            os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        )
        self._langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
        self._langsmith_project = os.getenv("LANGSMITH_PROJECT")
        self._logger = logging.getLogger("alfred.telemetry")
        self._setup_logger()
        self._langsmith_client: Any = None
        self._runs: dict[str, str] = {}
        self._setup_langsmith()

    def _setup_logger(self) -> None:
        """Configurar logger local."""
        if not self._enabled:
            return

        log_level = os.getenv("ALFRED_LOG_LEVEL", "INFO").upper()
        self._logger.setLevel(getattr(logging, log_level, logging.INFO))

        if not self._logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def _setup_langsmith(self) -> None:
        """Configurar cliente LangSmith opcional de forma segura."""
        if not self._langsmith_tracing or not self._langsmith_api_key:
            return

        try:
            from langsmith import Client

            self._langsmith_client = Client()
        except Exception:
            self._langsmith_client = None
            if self._enabled:
                self._logger.warning("LangSmith configurado mas indisponible")

    def generate_trace_id(self) -> str:
        """Gerar ID de trace único para correlação."""
        return secrets.token_hex(8)

    def _sanitize_message(self, message: str | None) -> str | None:
        """Remover conteúdo sensível de mensagens."""
        if not message or self._disable_content_tracing:
            return None
        return message

    def _build_decision_hash(
        self, category: str, confidence: float, rationale: str
    ) -> str:
        """Construir hash para correlação sem expor conteúdo."""
        content = f"{category}:{confidence:.2f}:{rationale}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _log_event(self, level: int, message: str, extra: dict) -> None:
        """Registrar evento localmente e sincronizar metadados com LangSmith."""
        if not self._enabled:
            return
        self._logger.log(level, message, extra=extra)
        self._sync_langsmith(extra)

    def _sync_langsmith(self, extra: dict) -> None:
        """Sincronizar metadados do evento com LangSmith sem conteúdo bruto."""
        if self._langsmith_client is None:
            return

        try:
            trace_id = str(extra.get("trace_id") or "")
            run_id = self._runs.get(trace_id)
            metadata = {k: v for k, v in extra.items() if k != "trace_id"}

            if run_id is None:
                run_id = secrets.token_hex(8)
                self._langsmith_client.create_run(
                    id=run_id,
                    project_name=self._langsmith_project,
                    name=f"alfred-{trace_id}",
                    run_type="chain",
                    inputs={},
                    start_time=datetime.now(timezone.utc),
                    extra=metadata,
                    hide_inputs=True,
                    hide_outputs=True,
                )
                self._runs[trace_id] = run_id
            else:
                self._langsmith_client.update_run(run_id, extra=metadata)
        except Exception:
            self._langsmith_client = None
            if self._enabled:
                self._logger.warning("LangSmith tracing desativado por erro")

    def emit_request(
        self, session_id: str, trace_id: str, latency_ms: float | None = None
    ) -> None:
        """Emitir evento de requisição."""
        self._log_event(
            logging.INFO,
            "Request received",
            {
                "event_type": "alfred_request",
                "session_id": session_id,
                "trace_id": trace_id,
                "latency_ms": latency_ms,
                "alfred_requests_total": 1,
            },
        )

    def emit_classification(
        self,
        session_id: str,
        category: str,
        confidence: float,
        rationale_code: str,
        trace_id: str,
        latency_ms: float | None = None,
        llm_model: str | None = None,
    ) -> None:
        """Emitir evento de classificação de intenção."""
        decision_hash = self._build_decision_hash(category, confidence, rationale_code)

        self._log_event(
            logging.INFO,
            "Intent classification",
            {
                "event_type": "alfred_intent_classification",
                "session_id": session_id,
                "intent_category": category,
                "intent_confidence": confidence,
                "decision_hash": decision_hash,
                "trace_id": trace_id,
                "latency_ms": latency_ms,
                "llm_model": llm_model,
                "alfred_intent_classification_total": 1,
            },
        )

    def emit_safety_check(
        self,
        session_id: str,
        category: str,
        safety_status: str,
        decision_hash: str,
        trace_id: str,
    ) -> None:
        """Emitir evento de verificação de segurança."""
        log_level = (
            logging.WARNING if safety_status in ("BLOCK", "CONFIRM") else logging.INFO
        )

        self._log_event(
            log_level,
            "Safety check result",
            {
                "event_type": "alfred_safety_check",
                "session_id": session_id,
                "intent_category": category,
                "safety_status": safety_status,
                "decision_hash": decision_hash,
                "trace_id": trace_id,
                "alfred_blocked_requests_total": 1 if safety_status == "BLOCK" else 0,
                "alfred_confirmation_required_total": 1
                if safety_status == "CONFIRM"
                else 0,
            },
        )

    def emit_response(
        self,
        session_id: str,
        category: str,
        safety_status: str,
        decision_hash: str,
        trace_id: str,
        latency_ms: float | None = None,
    ) -> None:
        """Emitir evento de resposta final."""
        self._log_event(
            logging.INFO,
            "Response generated",
            {
                "event_type": "alfred_response",
                "session_id": session_id,
                "intent_category": category,
                "safety_status": safety_status,
                "decision_hash": decision_hash,
                "trace_id": trace_id,
                "latency_ms": latency_ms,
            },
        )

    def emit_event(self, event: TelemetryEvent) -> None:
        """Emitir evento estruturado."""
        extra: dict[str, Any] = {
            "event_type": event.event_type,
            "session_id": event.session_id,
            "intent_category": event.intent_category,
            "safety_status": event.safety_status,
            "decision_hash": event.decision_hash,
            "trace_id": event.trace_id,
        }

        if event.intent_confidence is not None:
            extra["intent_confidence"] = event.intent_confidence
            extra["alfred_router_confidence"] = event.intent_confidence

        if event.latency_ms is not None:
            extra["latency_ms"] = event.latency_ms
            extra["alfred_llm_latency_seconds"] = event.latency_ms / 1000.0

        if event.llm_model is not None:
            extra["llm_model"] = event.llm_model

        log_level = (
            logging.WARNING
            if event.safety_status in ("BLOCK", "CONFIRM")
            else logging.INFO
        )
        self._log_event(log_level, "Event emitted", extra)

    def trace_disabled(self) -> bool:
        """Verificar se tracing está desabilitado."""
        return not self._enabled or self._disable_content_tracing


_client: TelemetryClient | None = None


def get_telemetry_client() -> TelemetryClient:
    """Obter instância singleton do cliente de telemetry."""
    global _client
    if _client is None:
        enabled = os.getenv("ALFRED_TELEMETRY_ENABLED", "true").lower() == "true"
        disable_content = (
            os.getenv("ALFRED_DISABLE_CONTENT_TRACING", "true").lower() == "true"
        )
        _client = TelemetryClient(
            enabled=enabled, disable_content_tracing=disable_content
        )
    return _client


def create_event(
    event_type: str,
    session_id: str,
    intent_category: str,
    safety_status: str,
    decision_hash: str,
    trace_id: str,
    intent_confidence: float | None = None,
    latency_ms: float | None = None,
    llm_model: str | None = None,
) -> TelemetryEvent:
    """Criar evento de telemetry."""
    return TelemetryEvent(
        event_type=event_type,
        session_id=session_id,
        intent_category=intent_category,
        safety_status=safety_status,
        decision_hash=decision_hash,
        trace_id=trace_id,
        intent_confidence=intent_confidence,
        latency_ms=latency_ms,
        llm_model=llm_model,
    )
