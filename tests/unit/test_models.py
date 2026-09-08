"""Testes unitários para o módulo models."""

from datetime import datetime, timedelta

import pytest

from alfred.models import (
    AssistantRequest,
    AssistantResponse,
    Channel,
    IntentCategory,
    IntentDecision,
    IntentRequest,
    IntentResponse,
    OutputFormat,
    SafetyDecision,
    SafetyStatus,
    SessionContext,
    SessionStoreConfig,
    SessionTurn,
)


class TestAssistantRequest:
    """Testes para AssistantRequest."""

    def test_assistant_request_creation(self):
        """Deve criar AssistantRequest válido."""
        request = AssistantRequest(
            message="Teste",
            session_id="test-123",
            channel="cli",
            output_format="text",
            interactive_confirmation=True,
            trace_enabled=True
        )

        assert request.message == "Teste"
        assert request.session_id == "test-123"
        assert request.channel == "cli"
        assert request.output_format == "text"

    def test_assistant_request_default_values(self):
        """Deve usar valores padrão corretamente."""
        request = AssistantRequest(
            message="Teste",
            session_id="test-123"
        )

        assert request.channel == "cli"
        assert request.output_format == "text"
        assert request.interactive_confirmation is True
        assert request.trace_enabled is True

    def test_assistant_request_validation_empty_message(self):
        """Deve aceitar mensagem vazia (validação será feita na CLI)."""
        request = AssistantRequest(
            message="",
            session_id="test-123"
        )
        assert request.message == ""


class TestIntentDecision:
    """Testes para IntentDecision."""

    def test_intent_decision_creation(self):
        """Deve criar IntentDecision válido."""
        decision = IntentDecision(
            category="CHITCHAT",
            confidence=0.95,
            rationale_code="greeting_detected",
            required_clarification=None,
            simulated_tool_name=None,
            risk_labels=[]
        )

        assert decision.category == "CHITCHAT"
        assert decision.confidence == 0.95
        assert decision.risk_labels == []

    def test_intent_decision_with_risk_labels(self):
        """Deve aceitar rótulos de risco."""
        decision = IntentDecision(
            category="CLOUD_TASK",
            confidence=0.85,
            rationale_code="task_detected",
            required_clarification=None,
            simulated_tool_name="web_search",
            risk_labels=["cost", "external_api"]
        )

        assert len(decision.risk_labels) == 2

    def test_intent_decision_confidence_range(self):
        """Deve aceitar confiança entre 0 e 1."""
        with pytest.raises(ValueError):
            IntentDecision(
                category="TEST",
                confidence=1.5,
                rationale_code="test",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[]
            )

    def test_intent_decision_hash_deterministic(self):
        """Deve gerar hash determinístico de 16 caracteres."""
        decision_a = IntentDecision(
            category=IntentCategory.CHITCHAT,
            confidence=0.95,
            rationale_code="greeting",
        )
        decision_b = IntentDecision(
            category=IntentCategory.CHITCHAT,
            confidence=0.95,
            rationale_code="greeting",
        )
        different = IntentDecision(
            category=IntentCategory.LOCAL_TASK,
            confidence=0.95,
            rationale_code="greeting",
        )

        assert decision_a.decision_hash == decision_b.decision_hash
        assert len(decision_a.decision_hash) == 16
        assert decision_a.decision_hash != different.decision_hash


class TestSafetyDecision:
    """Testes para SafetyDecision."""

    def test_safety_decision_allow(self):
        """Deve criar decisão ALLOW."""
        decision = SafetyDecision(
            status="ALLOW",
            reason_code="no_risk_detected",
            human_message="Solicitação aprovada."
        )

        assert decision.status == "ALLOW"

    def test_safety_decision_confirm(self):
        """Deve criar decisão CONFIRM."""
        decision = SafetyDecision(
            status="CONFIRM",
            reason_code="sensitive_operation",
            human_message="Requer confirmação."
        )

        assert decision.status == "CONFIRM"

    def test_safety_decision_block(self):
        """Deve criar decisão BLOCK."""
        decision = SafetyDecision(
            status="BLOCK",
            reason_code="blocked_category",
            human_message="Bloqueado por segurança."
        )

        assert decision.status == "BLOCK"


class TestAssistantResponse:
    """Testes para AssistantResponse."""

    def test_assistant_response_creation(self):
        """Deve criar AssistantResponse válido."""
        response = AssistantResponse(
            text="Resposta de teste",
            category="CHITCHAT",
            safety_status="ALLOW",
            session_id="test-123"
        )

        assert response.text == "Resposta de teste"
        assert response.category == "CHITCHAT"
        assert response.safety_status == "ALLOW"
        assert response.session_id == "test-123"

    def test_assistant_response_with_metadata(self):
        """Deve aceitar metadados."""
        response = AssistantResponse(
            text="Resposta com metadados",
            category="CLOUD_TASK",
            safety_status="ALLOW",
            session_id="test-123",
            metadata={"key": "value"}
        )

        assert response.metadata == {"key": "value"}

    def test_assistant_response_with_json_payload(self):
        """Deve aceitar payload JSON."""
        response = AssistantResponse(
            text="Resposta",
            category="CLOUD_TASK",
            safety_status="ALLOW",
            session_id="test-123",
            json_payload={"result": "data"}
        )

        assert response.json_payload == {"result": "data"}


class TestIntentCategory:
    """Testes para enum de categorias de intenção."""

    def test_intent_categories(self):
        """Deve ter todas as categorias esperadas."""
        assert IntentCategory.CHITCHAT.value == "CHITCHAT"
        assert IntentCategory.CLOUD_TASK.value == "CLOUD_TASK"
        assert IntentCategory.LOCAL_TASK.value == "LOCAL_TASK"
        assert IntentCategory.AMBIGUOUS.value == "AMBIGUOUS"
        assert IntentCategory.BLOCKED.value == "BLOCKED"
        assert IntentCategory.OUT_OF_SCOPE.value == "OUT_OF_SCOPE"


class TestSafetyStatus:
    """Testes para enum de status de segurança."""

    def test_safety_statuses(self):
        """Deve ter todos os status esperados."""
        assert SafetyStatus.ALLOW.value == "ALLOW"
        assert SafetyStatus.CONFIRM.value == "CONFIRM"
        assert SafetyStatus.BLOCK.value == "BLOCK"


class TestChannel:
    """Testes para enum de canais."""

    def test_channels(self):
        """Deve ter todos os canais esperados."""
        assert Channel.CLI.value == "cli"
        assert Channel.WHATSAPP.value == "whatsapp"


class TestOutputFormat:
    """Testes para enum de formatos de saída."""

    def test_output_formats(self):
        """Deve ter todos os formatos esperados."""
        assert OutputFormat.TEXT.value == "text"
        assert OutputFormat.JSON.value == "json"


class TestSessionTurn:
    """Testes para SessionTurn."""

    def test_session_turn_creation(self):
        """Deve criar SessionTurn válido."""
        now = datetime.now()
        expires = now + timedelta(hours=2)

        turn = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CHITCHAT,
            summary="Saudação inicial",
            decision_hash="abc123",
            category_label="Greeting",
            risk_labels=[]
        )

        assert turn.category == IntentCategory.CHITCHAT
        assert turn.summary == "Saudação inicial"
        assert turn.decision_hash == "abc123"

    def test_session_turn_with_risk_labels(self):
        """Deve aceitar rótulos de risco."""
        now = datetime.now()
        expires = now + timedelta(hours=2)

        turn = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CLOUD_TASK,
            summary="Busca na web",
            decision_hash="def456",
            risk_labels=["cost", "external_api"]
        )

        assert len(turn.risk_labels) == 2


class TestSessionContext:
    """Testes para SessionContext."""

    def test_session_context_creation(self):
        """Deve criar SessionContext válido."""
        now = datetime.now()
        expires = now + timedelta(hours=2)

        context = SessionContext(
            session_id="test-session",
            created_at=now,
            expires_at=expires,
            version="1.0"
        )

        assert context.session_id == "test-session"
        assert context.version == "1.0"
        assert context.turns == []

    def test_session_context_with_turns(self):
        """Deve aceitar lista de turnos."""
        now = datetime.now()
        expires = now + timedelta(hours=2)

        turn = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CHITCHAT,
            summary="Saudação",
            decision_hash="abc123"
        )

        context = SessionContext(
            session_id="test-session",
            turns=[turn],
            created_at=now,
            expires_at=expires
        )

        assert len(context.turns) == 1
        assert context.turns[0].summary == "Saudação"

    def test_session_context_version_default(self):
        """Deve ter versão padrão."""
        now = datetime.now()
        expires = now + timedelta(hours=2)

        context = SessionContext(
            session_id="test-session",
            created_at=now,
            expires_at=expires
        )

        assert context.version == "1.0"


class TestSessionStoreConfig:
    """Testes para SessionStoreConfig."""

    def test_session_store_config_defaults(self):
        """Deve usar valores padrão."""
        config = SessionStoreConfig()

        assert config.ttl_seconds == 7200
        assert config.max_turns == 10
        assert config.storage_path is None

    def test_session_store_config_custom(self):
        """Deve aceitar valores customizados."""
        config = SessionStoreConfig(
            ttl_seconds=3600,
            max_turns=5,
            storage_path="/tmp/sessions"
        )

        assert config.ttl_seconds == 3600
        assert config.max_turns == 5
        assert config.storage_path == "/tmp/sessions"


class TestIntentRequest:
    """Testes para IntentRequest."""

    def test_intent_request_creation(self):
        """Deve criar IntentRequest válido."""
        request = IntentRequest(
            message="Olá",
            session_id="test-123",
            channel=Channel.CLI
        )

        assert request.message == "Olá"
        assert request.channel == Channel.CLI
        assert request.history == []

    def test_intent_request_with_history(self):
        """Deve aceitar histórico."""
        request = IntentRequest(
            message="Continua",
            session_id="test-123",
            channel=Channel.CLI,
            history=["Olá", "Como vai?"]
        )

        assert len(request.history) == 2


class TestIntentResponse:
    """Testes para IntentResponse."""

    def test_intent_response_creation(self):
        """Deve criar IntentResponse válido."""
        response = IntentResponse(
            category=IntentCategory.CHITCHAT,
            confidence=0.95,
            rationale_code="greeting_detected"
        )

        assert response.category == IntentCategory.CHITCHAT
        assert response.confidence == 0.95
        assert response.simulated_tool is None

    def test_intent_response_with_tool_and_risk(self):
        """Deve aceitar tool e rótulos de risco."""
        response = IntentResponse(
            category=IntentCategory.CLOUD_TASK,
            confidence=0.85,
            rationale_code="task_detected",
            simulated_tool="web_search",
            risk_labels=["cost", "external_api"]
        )

        assert response.simulated_tool == "web_search"
        assert len(response.risk_labels) == 2
