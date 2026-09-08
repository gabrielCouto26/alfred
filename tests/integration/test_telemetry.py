"""Testes de integração para telemetry com AssistantService."""

from unittest.mock import MagicMock, patch

import pytest

from alfred.app.assistant_service import AssistantServiceImpl
from alfred.memory.session_store import LocalSessionStore
from alfred.models import (
    AssistantRequest,
    IntentCategory,
    IntentDecision,
    SessionStoreConfig,
)
from alfred.routing.intent_router import IntentRouterImpl
from alfred.safety.policy import DeterministicSafetyPolicy
from alfred.tools.simulated_registry import SimulatedToolsRegistry


class SpyTelemetry:
    """Fake de telemetry que registra todos os eventos emitidos."""

    def __init__(self):
        self.events: list[tuple[str, dict]] = []

    def _record(self, name: str, args: tuple, kwargs: dict) -> None:
        merged = dict(kwargs)
        for index, value in enumerate(args):
            merged[f"arg{index}"] = value
        self.events.append((name, merged))

    def generate_trace_id(self) -> str:
        return "trace-spy"

    def emit_request(self, *args, **kwargs) -> None:
        self._record("emit_request", args, kwargs)

    def emit_classification(self, *args, **kwargs) -> None:
        self._record("emit_classification", args, kwargs)

    def emit_safety_check(self, *args, **kwargs) -> None:
        self._record("emit_safety_check", args, kwargs)

    def emit_response(self, *args, **kwargs) -> None:
        self._record("emit_response", args, kwargs)

    def trace_disabled(self) -> bool:
        return False

    @property
    def raw_values(self) -> list[str]:
        values: list[str] = []
        for _, kwargs in self.events:
            for value in kwargs.values():
                if isinstance(value, str):
                    values.append(value)
                elif isinstance(value, (int, float)):
                    values.append(str(value))
        return values


@pytest.fixture
def temp_dir(tmp_path):
    return tmp_path


@pytest.fixture
def session_store(temp_dir):
    config = SessionStoreConfig(storage_path=str(temp_dir), ttl_seconds=7200)
    store = LocalSessionStore(config=config)
    return store


@pytest.fixture
def full_assistant_service(session_store, temp_dir):
    with patch("alfred.routing.intent_router.create_llm_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        intent_router = IntentRouterImpl()
        intent_router.llm_client = mock_client
        safety = DeterministicSafetyPolicy()
        registry = SimulatedToolsRegistry()

        service = AssistantServiceImpl(
            intent_router=intent_router,
            safety_policy=safety,
            session_store=session_store,
            simulated_tools_registry=registry,
        )
        return service


class TestTelemetryIntegration:
    @pytest.mark.integration
    def test_integration_no_raw_message_in_telemetry(
        self, full_assistant_service, session_store
    ):
        """Garantir que conteúdo bruto nunca chega aos eventos de telemetry."""
        full_assistant_service._intent_router.llm_client.generate.return_value = (
            IntentDecision(
                category=IntentCategory.CHITCHAT,
                confidence=0.95,
                rationale_code="greeting_detected",
            )
        )
        spy = SpyTelemetry()

        with patch(
            "alfred.observability.get_telemetry_client", return_value=spy
        ):
            request = AssistantRequest(
                message="Olá, minha senha é 123456!",
                session_id="telemetry_test_3",
                channel="cli",
                trace_enabled=True,
            )

            full_assistant_service.handle(request)

            assert spy.events, "Nenhún evento de telemetry foi emitido"
            for value in spy.raw_values:
                assert "123456" not in value
                assert "Olá" not in value

    @pytest.mark.integration
    def test_integration_telemetry_emit_events(
        self, full_assistant_service, session_store
    ):
        """Verificar que os eventos esperados são emitidos no fluxo."""
        full_assistant_service._intent_router.llm_client.generate.return_value = (
            IntentDecision(
                category=IntentCategory.CHITCHAT,
                confidence=0.95,
                rationale_code="greeting_detected",
            )
        )
        spy = SpyTelemetry()

        with patch(
            "alfred.observability.get_telemetry_client", return_value=spy
        ):
            request = AssistantRequest(
                message="Olá, Alfred!",
                session_id="telemetry_test_1",
                channel="cli",
                trace_enabled=True,
            )

            full_assistant_service.handle(request)

            event_types = [name for name, _ in spy.events]
            assert "emit_request" in event_types
            assert "emit_classification" in event_types
            assert "emit_safety_check" in event_types
            assert "emit_response" in event_types

    @pytest.mark.integration
    def test_integration_trace_disabled_no_events(
        self, full_assistant_service, session_store
    ):
        """Verificar que --no-trace suprime todos los eventos de telemetry."""
        full_assistant_service._intent_router.llm_client.generate.return_value = (
            IntentDecision(
                category=IntentCategory.CHITCHAT,
                confidence=0.95,
                rationale_code="greeting_detected",
            )
        )
        spy = SpyTelemetry()

        with patch(
            "alfred.observability.get_telemetry_client", return_value=spy
        ):
            request = AssistantRequest(
                message="Olá, Alfred!",
                session_id="telemetry_test_2",
                channel="cli",
                trace_enabled=False,
            )

            full_assistant_service.handle(request)

            assert spy.events == []
