"""Testes de integração para os contratos internos."""

import pytest

from alfred.models import (
    AssistantRequest,
    AssistantResponse,
    IntentDecision,
    IntentRequest,
    IntentResponse,
    SafetyDecision,
    SessionContext,
    SessionTurn,
    IntentCategory,
    SafetyStatus,
    Channel,
)


class TestRequestResponseFlow:
    """Testes de fluxo completo request-response."""
    
    def test_full_request_to_response_flow(self):
        """Deve permitir fluxo completo de request para response."""
        request = AssistantRequest(
            message="Olá, você pode me ajudar?",
            session_id="test-123",
            channel=Channel.CLI,
            output_format="text",
            interactive_confirmation=True,
            trace_enabled=True
        )
        
        decision = IntentDecision(
            category=IntentCategory.CHITCHAT,
            confidence=0.95,
            rationale_code="greeting_detected",
            required_clarification=None,
            simulated_tool_name=None,
            risk_labels=[]
        )
        
        safety = SafetyDecision(
            status=SafetyStatus.ALLOW,
            reason_code="no_risk_detected",
            human_message="Solicitação aprovada."
        )
        
        response = AssistantResponse(
            text="Olá! Claro que posso ajudar. O que você precisa?",
            category=decision.category,
            safety_status=safety.status,
            session_id=request.session_id,
            metadata={
                "confidence": decision.confidence,
                "rationale_code": decision.rationale_code
            }
        )
        
        assert response.session_id == request.session_id
        assert response.category == IntentCategory.CHITCHAT
        assert response.safety_status == SafetyStatus.ALLOW
        assert response.metadata["confidence"] == 0.95


class TestSessionTurnPersistence:
    """Testes de persistência de turnos de sessão."""
    
    def test_session_turn_serialization(self):
        """Deve permitir serialização e desserialização de SessionTurn."""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        turn = SessionTurn(
            created_at=now,
            expires_at=now + timedelta(hours=2),
            category=IntentCategory.CHITCHAT,
            summary="Saudação inicial",
            decision_hash="abc123",
            category_label="Greeting",
            risk_labels=["low_risk"]
        )
        
        data = turn.model_dump()
        
        assert data["category"] == "CHITCHAT"
        assert data["summary"] == "Saudação inicial"
        assert data["decision_hash"] == "abc123"
    
    def test_session_context_serialization(self):
        """Deve permitir serialização e desserialização de SessionContext."""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        turn = SessionTurn(
            created_at=now,
            expires_at=now + timedelta(hours=2),
            category=IntentCategory.CHITCHAT,
            summary="Saudação",
            decision_hash="abc123"
        )
        
        context = SessionContext(
            session_id="test-123",
            turns=[turn],
            created_at=now,
            expires_at=now + timedelta(hours=2),
            version="1.0"
        )
        
        data = context.model_dump()
        
        assert data["session_id"] == "test-123"
        assert len(data["turns"]) == 1
        assert data["version"] == "1.0"


class TestIntentFlow:
    """Testes de fluxo de classificação de intenção."""
    
    def test_intent_request_to_response(self):
        """Deve permitir fluxo completo de IntentRequest para IntentResponse."""
        request = IntentRequest(
            message="Preciso fazer uma busca na web",
            session_id="test-123",
            channel=Channel.CLI,
            history=["Olá", "O que você pode fazer?"]
        )
        
        response = IntentResponse(
            category=IntentCategory.CLOUD_TASK,
            confidence=0.88,
            rationale_code="search_intent_detected",
            requires_clarification=False,
            simulated_tool="web_search",
            risk_labels=["cost", "external_api"]
        )
        
        assert response.category == IntentCategory.CLOUD_TASK
        assert response.simulated_tool == "web_search"
        assert len(response.risk_labels) == 2
    
    def test_intent_request_with_clarification(self):
        """Deve suportar solicitação de clarificação."""
        request = IntentRequest(
            message="Me ajuda",
            session_id="test-123",
            channel=Channel.CLI
        )
        
        response = IntentResponse(
            category=IntentCategory.AMBIGUOUS,
            confidence=0.45,
            rationale_code="insufficient_context",
            requires_clarification=True,
            simulated_tool=None,
            risk_labels=[]
        )
        
        assert response.category == IntentCategory.AMBIGUOUS
        assert response.requires_clarification is True


class TestSafetyDecisionIntegration:
    """Testes de integração com política de segurança."""
    
    def test_safety_decision_blocked_request(self):
        """Deve bloquear solicitações com risco alto."""
        intent = IntentDecision(
            category=IntentCategory.LOCAL_TASK,
            confidence=0.92,
            rationale_code="rm_command_detected",
            required_clarification=None,
            simulated_tool_name=None,
            risk_labels=["destructive", "irreversible"]
        )
        
        safety = SafetyDecision(
            status=SafetyStatus.BLOCK,
            reason_code="destructive_command",
            human_message="Ação bloqueada: comando destrutivo detectado."
        )
        
        assert safety.status == SafetyStatus.BLOCK
        assert "destructive" in intent.risk_labels
    
    def test_safety_decision_confirmation_required(self):
        """Deve exigir confirmação para operações sensíveis."""
        intent = IntentDecision(
            category=IntentCategory.LOCAL_TASK,
            confidence=0.85,
            rationale_code="file_operation",
            required_clarification=None,
            simulated_tool_name="file_editor",
            risk_labels=["data_modification"]
        )
        
        safety = SafetyDecision(
            status=SafetyStatus.CONFIRM,
            reason_code="sensitive_operation",
            human_message="Requer confirmação: operação de arquivo detectada."
        )
        
        assert safety.status == SafetyStatus.CONFIRM
        assert len(intent.risk_labels) == 1


class TestChannelConsistency:
    """Testes de consistência entre canais."""
    
    def test_cli_and_whatsapp_consistency(self):
        """Deve manter consistência entre CLI e WhatsApp."""
        cli_request = AssistantRequest(
            message="Olá",
            session_id="cli-session-1",
            channel=Channel.CLI
        )
        
        wa_request = AssistantRequest(
            message="Olá",
            session_id="wa-session-1",
            channel=Channel.WHATSAPP
        )
        
        assert cli_request.message == wa_request.message
        assert cli_request.channel != wa_request.channel
        assert cli_request.output_format == wa_request.output_format
