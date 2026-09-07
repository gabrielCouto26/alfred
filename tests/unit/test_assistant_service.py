"""Testes unitários para AssistantService."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from alfred.app.assistant_service import AssistantServiceImpl
from alfred.models import (
    AssistantRequest,
    AssistantResponse,
    IntentCategory,
    IntentDecision,
    SafetyDecision,
    SafetyStatus,
    SessionContext,
    SimulatedToolResponse,
)


@pytest.fixture
def mock_router():
    return MagicMock()


@pytest.fixture
def mock_safety():
    return MagicMock()


@pytest.fixture
def mock_session_store():
    store = MagicMock()
    store.load.return_value = SessionContext(
        session_id="test_session",
        turns=[],
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=2),
        version="1.0",
    )
    return store


@pytest.fixture
def mock_registry():
    registry = MagicMock()
    registry.simulate_cloud_task.return_value = SimulatedToolResponse(
        status="PREPARED",
        intention="simulated",
        requires_confirmation=True,
        human_message="Simulado: tarefa em nuvem 'enviar_email'",
    )
    registry.simulate_local_task.return_value = SimulatedToolResponse(
        status="PREPARED",
        intention="simulated",
        requires_confirmation=True,
        human_message="Simulado: tarefa local 'gerar_relatorio'",
    )
    return registry


@pytest.fixture
def assistant_service(mock_router, mock_safety, mock_session_store, mock_registry):
    return AssistantServiceImpl(
        intent_router=mock_router,
        safety_policy=mock_safety,
        session_store=mock_session_store,
        simulated_tools_registry=mock_registry,
    )


class TestAssistantServiceImpl:
    def test_handle_chitchat_success(
        self, assistant_service, mock_router, mock_safety, mock_session_store
    ):
        mock_router.classify.return_value = IntentDecision(
            category=IntentCategory.CHITCHAT,
            confidence=0.95,
            rationale_code="greeting_detected",
        )
        mock_safety.evaluate.return_value = SafetyDecision(
            status=SafetyStatus.ALLOW, reason_code="none", human_message=""
        )

        request = AssistantRequest(
            message="Olá, Alfred!", session_id="test_session", channel="cli"
        )

        response = assistant_service.handle(request)

        assert isinstance(response, AssistantResponse)
        assert response.category == IntentCategory.CHITCHAT
        assert response.safety_status == SafetyStatus.ALLOW
        assert "Olá" in response.text or "Como posso ajudar" in response.text

    def test_handle_cloud_task_success(
        self, assistant_service, mock_router, mock_safety, mock_session_store
    ):
        mock_router.classify.return_value = IntentDecision(
            category=IntentCategory.CLOUD_TASK,
            confidence=0.85,
            rationale_code="cloud_task_detected",
            simulated_tool_name="enviar_email",
        )
        mock_safety.evaluate.return_value = SafetyDecision(
            status=SafetyStatus.ALLOW, reason_code="none", human_message=""
        )

        request = AssistantRequest(
            message="Envie um email para cliente",
            session_id="test_session",
            channel="cli",
        )

        response = assistant_service.handle(request)

        assert isinstance(response, AssistantResponse)
        assert response.category == IntentCategory.CLOUD_TASK
        assert "Simulado" in response.text
        assert "tarefa em nuvem" in response.text

    def test_handle_local_task_success(
        self, assistant_service, mock_router, mock_safety, mock_session_store
    ):
        mock_router.classify.return_value = IntentDecision(
            category=IntentCategory.LOCAL_TASK,
            confidence=0.85,
            rationale_code="local_task_detected",
            simulated_tool_name="gerar_relatorio",
        )
        mock_safety.evaluate.return_value = SafetyDecision(
            status=SafetyStatus.ALLOW, reason_code="none", human_message=""
        )

        request = AssistantRequest(
            message="Gere o relatório mensal", session_id="test_session", channel="cli"
        )

        response = assistant_service.handle(request)

        assert isinstance(response, AssistantResponse)
        assert response.category == IntentCategory.LOCAL_TASK
        assert "Simulado" in response.text
        assert "tarefa local" in response.text

    def test_handle_ambiguous(
        self, assistant_service, mock_router, mock_safety, mock_session_store
    ):
        mock_router.classify.return_value = IntentDecision(
            category=IntentCategory.AMBIGUOUS,
            confidence=0.4,
            rationale_code="insufficient_info",
            required_clarification="Pode especificar qual ação você deseja?",
        )
        mock_safety.evaluate.return_value = SafetyDecision(
            status=SafetyStatus.ALLOW, reason_code="none", human_message=""
        )

        request = AssistantRequest(
            message="Faz aquela coisa", session_id="test_session", channel="cli"
        )

        response = assistant_service.handle(request)

        assert isinstance(response, AssistantResponse)
        assert response.category == IntentCategory.AMBIGUOUS
        assert "Pode especificar" in response.text

    def test_handle_blocked_by_safety(
        self, assistant_service, mock_router, mock_safety, mock_session_store
    ):
        mock_router.classify.return_value = IntentDecision(
            category=IntentCategory.LOCAL_TASK,
            confidence=0.9,
            rationale_code="command_detected",
            simulated_tool_name="rm_rf",
            risk_labels=["destructive"],
        )
        mock_safety.evaluate.return_value = SafetyDecision(
            status=SafetyStatus.BLOCK,
            reason_code="destructive_command",
            human_message="Bloqueado: comando destrutivo detectado",
        )

        request = AssistantRequest(
            message="rm -rf /tmp", session_id="test_session", channel="cli"
        )

        response = assistant_service.handle(request)

        assert isinstance(response, AssistantResponse)
        assert response.safety_status == SafetyStatus.BLOCK
        assert "Bloqueado" in response.text

    def test_handle_out_of_scope(
        self, assistant_service, mock_router, mock_safety, mock_session_store
    ):
        mock_router.classify.return_value = IntentDecision(
            category=IntentCategory.OUT_OF_SCOPE,
            confidence=0.7,
            rationale_code="feature_not_implemented",
        )
        mock_safety.evaluate.return_value = SafetyDecision(
            status=SafetyStatus.ALLOW, reason_code="none", human_message=""
        )

        request = AssistantRequest(
            message="Resolva problemas complexos de servidores",
            session_id="test_session",
            channel="cli",
        )

        response = assistant_service.handle(request)

        assert isinstance(response, AssistantResponse)
        assert response.category == IntentCategory.OUT_OF_SCOPE
        assert "fora de escopo" in response.text.lower()

    def test_handle_confirmation_required(
        self, assistant_service, mock_router, mock_safety, mock_session_store
    ):
        mock_router.classify.return_value = IntentDecision(
            category=IntentCategory.LOCAL_TASK,
            confidence=0.9,
            rationale_code="sensitive_command",
            simulated_tool_name="rm",
            risk_labels=["destructive"],
        )
        mock_safety.evaluate.return_value = SafetyDecision(
            status=SafetyStatus.CONFIRM,
            reason_code="dangerous_command",
            human_message="Atenção: este comando pode ser perigoso. Deseja continuar?",
        )

        request = AssistantRequest(
            message="rm arquivo.txt",
            session_id="test_session",
            channel="cli",
            interactive_confirmation=True,
        )

        with patch("alfred.app.assistant_service.input", return_value="s"):
            response = assistant_service.handle(request)

        assert isinstance(response, AssistantResponse)
        assert "Simulado" in response.text

    def test_handle_confirmation_declined(
        self, assistant_service, mock_router, mock_safety, mock_session_store
    ):
        mock_router.classify.return_value = IntentDecision(
            category=IntentCategory.LOCAL_TASK,
            confidence=0.9,
            rationale_code="sensitive_command",
            simulated_tool_name="rm",
            risk_labels=["destructive"],
        )
        mock_safety.evaluate.return_value = SafetyDecision(
            status=SafetyStatus.CONFIRM,
            reason_code="dangerous_command",
            human_message="Atenção: este comando pode ser perigoso. Deseja continuar?",
        )

        request = AssistantRequest(
            message="rm arquivo.txt",
            session_id="test_session",
            channel="cli",
            interactive_confirmation=True,
        )

        with patch("alfred.app.assistant_service.input", return_value="n"):
            response = assistant_service.handle(request)

        assert isinstance(response, AssistantResponse)
        assert response.safety_status == SafetyStatus.BLOCK

    def test_handle_error_recovery(
        self, assistant_service, mock_router, mock_safety, mock_session_store
    ):
        mock_router.classify.side_effect = Exception("LLM timeout")

        request = AssistantRequest(
            message="Teste de erro", session_id="test_session", channel="cli"
        )

        response = assistant_service.handle(request)

        assert isinstance(response, AssistantResponse)
        assert response.category == IntentCategory.AMBIGUOUS
        assert response.safety_status == SafetyStatus.BLOCK
        assert "Erro" in response.text

    def test_persist_session_on_all_paths(
        self, assistant_service, mock_router, mock_safety, mock_session_store
    ):
        mock_router.classify.return_value = IntentDecision(
            category=IntentCategory.CHITCHAT,
            confidence=0.95,
            rationale_code="greeting",
        )
        mock_safety.evaluate.return_value = SafetyDecision(
            status=SafetyStatus.ALLOW, reason_code="none", human_message=""
        )

        request = AssistantRequest(
            message="Teste", session_id="persist_test", channel="cli"
        )

        assistant_service.handle(request)

        assert mock_session_store.append.called
        call_args = mock_session_store.append.call_args
        assert call_args[0][0] == "persist_test"
        turn = call_args[0][1]
        assert hasattr(turn, "category")
        assert hasattr(turn, "summary")

    def test_no_raw_message_in_session(
        self, assistant_service, mock_router, mock_safety, mock_session_store
    ):
        mock_router.classify.return_value = IntentDecision(
            category=IntentCategory.CHITCHAT,
            confidence=0.95,
            rationale_code="greeting",
        )
        mock_safety.evaluate.return_value = SafetyDecision(
            status=SafetyStatus.ALLOW, reason_code="none", human_message=""
        )

        request = AssistantRequest(
            message="Senha secreta 12345", session_id="secret_test", channel="cli"
        )

        assistant_service.handle(request)

        call_args = mock_session_store.append.call_args
        turn = call_args[0][1]
        raw_message = "Senha secreta 12345"
        assert raw_message not in turn.summary
