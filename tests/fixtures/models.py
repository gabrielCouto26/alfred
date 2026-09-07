"""Teste fixtures para o Alfred."""

import pytest

from alfred.models import AssistantRequest, IntentDecision, SafetyDecision


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
