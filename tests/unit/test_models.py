"""Testes unitários para o módulo models."""

import pytest

from alfred.models import AssistantRequest, IntentDecision, SafetyDecision, AssistantResponse


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
