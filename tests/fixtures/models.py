"""Teste fixtures para o Alfred."""

import pytest
from datetime import datetime, timedelta

from alfred.models import (
    AssistantRequest,
    IntentDecision,
    SafetyDecision,
    SessionTurn,
    SessionContext,
    IntentRequest,
    IntentResponse,
    IntentCategory,
    SafetyStatus,
)


@pytest.fixture
def sample_assistant_request() -> AssistantRequest:
    """Fixture de solicitação de exemplo."""
    return AssistantRequest(
        message="Olá, você pode me ajudar?",
        session_id="test-session-1",
        channel="cli",
        output_format="text",
        interactive_confirmation=True,
        trace_enabled=True
    )


@pytest.fixture
def sample_intent_decision() -> IntentDecision:
    """Fixture de decisão de intenção de exemplo."""
    return IntentDecision(
        category="CHITCHAT",
        confidence=0.95,
        rationale_code="greeting_detected",
        required_clarification=None,
        simulated_tool_name=None,
        risk_labels=[]
    )


@pytest.fixture
def sample_safety_decision() -> SafetyDecision:
    """Fixture de decisão de segurança de exemplo."""
    return SafetyDecision(
        status="ALLOW",
        reason_code="no_risk_detected",
        human_message="Solicitação aprovada."
    )


@pytest.fixture
def sample_session_turn() -> SessionTurn:
    """Fixture de turno de sessão de exemplo."""
    now = datetime.now()
    return SessionTurn(
        created_at=now,
        expires_at=now + timedelta(hours=2),
        category=IntentCategory.CHITCHAT,
        summary="Saudação inicial",
        decision_hash="abc123"
    )


@pytest.fixture
def sample_session_context(sample_session_turn: SessionTurn) -> SessionContext:
    """Fixture de contexto de sessão de exemplo."""
    now = datetime.now()
    return SessionContext(
        session_id="test-session-1",
        turns=[sample_session_turn],
        created_at=now,
        expires_at=now + timedelta(hours=2)
    )


@pytest.fixture
def sample_intent_request() -> IntentRequest:
    """Fixture de solicitação de intenção de exemplo."""
    return IntentRequest(
        message="O que você pode fazer?",
        session_id="test-session-1",
        channel="cli"
    )


@pytest.fixture
def sample_intent_response() -> IntentResponse:
    """Fixture de resposta de intenção de exemplo."""
    return IntentResponse(
        category=IntentCategory.CHITCHAT,
        confidence=0.92,
        rationale_code="question_detected",
        requires_clarification=False,
        simulated_tool=None,
        risk_labels=[]
    )
