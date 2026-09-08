"""Testes de integração para AssistantService."""

from unittest.mock import MagicMock, patch

import pytest

from alfred.app.__init__ import SimulatedToolsRegistry, create_assistant_service
from alfred.app.assistant_service import AssistantServiceImpl
from alfred.memory.session_store import LocalSessionStore
from alfred.models import (
    AssistantRequest,
    IntentCategory,
    IntentDecision,
    SafetyStatus,
    SessionStoreConfig,
)
from alfred.routing.intent_router import IntentRouterImpl
from alfred.safety.policy import DeterministicSafetyPolicy


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
    mock_router = MagicMock(spec=IntentRouterImpl)
    mock_router.classify.return_value = IntentDecision(
        category=IntentCategory.CHITCHAT,
        confidence=0.95,
        rationale_code="mocked",
    )
    safety = DeterministicSafetyPolicy()
    registry = SimulatedToolsRegistry()

    service = AssistantServiceImpl(
        intent_router=mock_router,
        safety_policy=safety,
        session_store=session_store,
        simulated_tools_registry=registry,
    )
    return service


def _set_classification(service, **kwargs) -> None:
    """Configurar la clasificación del router mockeado."""
    service._intent_router.classify.return_value = IntentDecision(**kwargs)


class TestAssistantServiceIntegration:
    @pytest.mark.integration
    def test_integration_flow_chitchat(self, full_assistant_service, session_store):
        request = AssistantRequest(
            message="Olá, Alfred!", session_id="integration_test_1", channel="cli"
        )

        response = full_assistant_service.handle(request)

        assert response.category == IntentCategory.CHITCHAT
        assert response.safety_status == SafetyStatus.ALLOW
        assert len(response.text) > 0

    @pytest.mark.integration
    def test_integration_flow_cloud_task(self, full_assistant_service, session_store):
        _set_classification(
            full_assistant_service,
            category=IntentCategory.CLOUD_TASK,
            confidence=0.9,
            rationale_code="cloud_task_detected",
            simulated_tool_name="schedule_meeting",
        )
        request = AssistantRequest(
            message="Agende uma reunião com equipe",
            session_id="integration_test_2",
            channel="cli",
        )

        response = full_assistant_service.handle(request)

        assert response.category == IntentCategory.CLOUD_TASK
        assert "Simulado" in response.text

    @pytest.mark.integration
    def test_integration_flow_local_task(self, full_assistant_service, session_store):
        _set_classification(
            full_assistant_service,
            category=IntentCategory.LOCAL_TASK,
            confidence=0.9,
            rationale_code="local_task_detected",
            simulated_tool_name="generate_report",
        )
        request = AssistantRequest(
            message="Gerar relatório de vendas",
            session_id="integration_test_3",
            channel="cli",
        )

        response = full_assistant_service.handle(request)

        assert response.category == IntentCategory.LOCAL_TASK
        assert "Simulado" in response.text

    @pytest.mark.integration
    def test_integration_flow_blocked(self, full_assistant_service, session_store):
        request = AssistantRequest(
            message="rm -rf /tmp/teste", session_id="integration_test_4", channel="cli"
        )

        response = full_assistant_service.handle(request)

        assert response.safety_status == SafetyStatus.BLOCK
        assert "Bloqueado" in response.text

    @pytest.mark.integration
    def test_integration_session_persistence(self, full_assistant_service, session_store):
        session_id = "integration_test_5"
        request = AssistantRequest(
            message="Olá!", session_id=session_id, channel="cli"
        )

        full_assistant_service.handle(request)

        context = session_store.load(session_id)
        assert context.session_id == session_id
        assert len(context.turns) > 0

    @pytest.mark.integration
    def test_integration_no_raw_message_persistence(
        self, full_assistant_service, session_store
    ):
        session_id = "integration_test_6"
        secret_message = "SenhaSuperSecreta123"
        request = AssistantRequest(
            message=secret_message, session_id=session_id, channel="cli"
        )

        full_assistant_service.handle(request)

        context = session_store.load(session_id)
        assert secret_message not in context.turns[0].summary

    @pytest.mark.integration
    def test_integration_factory_function(self, temp_dir):
        with patch("alfred.routing.intent_router.create_llm_client") as mock_create:
            mock_create.return_value = MagicMock()
            service = create_assistant_service()

        assert isinstance(service, AssistantServiceImpl)
        assert service._intent_router is not None
        assert service._safety_policy is not None
        assert service._session_store is not None
        assert service._simulated_tools_registry is not None
