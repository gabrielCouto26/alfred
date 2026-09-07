"""Testes de integração para política de segurança."""

import pytest

from alfred.models import (
    AssistantRequest,
    IntentDecision,
    SafetyDecision,
    IntentCategory,
    SafetyStatus,
    Channel,
)
from alfred.safety.policy import DeterministicSafetyPolicy


class TestSafetyPolicyIntegration:
    """Testes de integração para DeterministicSafetyPolicy."""

    def setup_method(self):
        """Inicializar política de segurança."""
        self.policy = DeterministicSafetyPolicy()

    def _create_request(self, message: str, session_id: str = "integration-test") -> AssistantRequest:
        """Criar AssistantRequest para teste."""
        return AssistantRequest(
            message=message,
            session_id=session_id,
            channel=Channel.CLI,
            output_format="text",
            interactive_confirmation=True,
            trace_enabled=True,
        )

    def _create_decision(
        self, category: IntentCategory = IntentCategory.CHITCHAT, risk_labels: list[str] = None
    ) -> IntentDecision:
        """Criar IntentDecision para teste."""
        if risk_labels is None:
            risk_labels = []
        return IntentDecision(
            category=category,
            confidence=0.95,
            rationale_code="test_rationale",
            required_clarification=None,
            simulated_tool_name=None,
            risk_labels=risk_labels,
        )

    def test_full_flow_dangerous_command(self):
        """Testar fluxo completo: request -> decision -> safety decision (BLOCK)."""
        request = self._create_request("rm -rf /var/log/*")
        decision = self._create_decision(category=IntentCategory.LOCAL_TASK)

        safety_decision = self.policy.evaluate(decision, request)

        assert safety_decision.status == SafetyStatus.BLOCK
        assert safety_decision.reason_code == "blocked_dangerous_command"
        assert "perigoso" in safety_decision.human_message.lower()

    def test_full_flow_sensitive_operation(self):
        """Testar fluxo completo: request -> decision -> safety decision (CONFIRM)."""
        request = self._create_request("excluir banco de dados de produção")
        decision = self._create_decision(category=IntentCategory.LOCAL_TASK)

        safety_decision = self.policy.evaluate(decision, request)

        assert safety_decision.status == SafetyStatus.CONFIRM
        assert safety_decision.reason_code == "sensitive_operation"

    def test_full_flow_risk_labels_integration(self):
        """Testar fluxo com risk_labels combinadas."""
        request = self._create_request("exportar dados sensíveis")
        decision = self._create_decision(
            category=IntentCategory.CLOUD_TASK,
            risk_labels=["private", "destructive"],
        )

        safety_decision = self.policy.evaluate(decision, request)

        assert safety_decision.status == SafetyStatus.CONFIRM
        assert "private" in safety_decision.reason_code

    def test_full_flow_allowed_operation(self):
        """Testar fluxo: operação permitida."""
        request = self._create_request("qual é a capital da França?")
        decision = self._create_decision(category=IntentCategory.CHITCHAT)

        safety_decision = self.policy.evaluate(decision, request)

        assert safety_decision.status == SafetyStatus.ALLOW
        assert safety_decision.reason_code == "no_risk_detected"

    def test_full_flow_blocked_by_router(self):
        """Testar fluxo: categoria BLOCKED."""
        request = self._create_request("qualquer coisa perigosa")
        decision = self._create_decision(category=IntentCategory.BLOCKED)

        safety_decision = self.policy.evaluate(decision, request)

        assert safety_decision.status == SafetyStatus.BLOCK
        assert safety_decision.reason_code == "blocked_by_router"

    def test_full_flow_out_of_scope(self):
        """Testar fluxo: categoria OUT_OF_SCOPE."""
        request = self._create_request("qualquer coisa")
        decision = self._create_decision(category=IntentCategory.OUT_OF_SCOPE)

        safety_decision = self.policy.evaluate(decision, request)

        assert safety_decision.status == SafetyStatus.BLOCK
        assert safety_decision.reason_code == "out_of_scope"

    def test_multiple_risk_labels_priority(self):
        """Testar prioridade quando múltiplos risk_labels presentes."""
        request = self._create_request("deletar banco e expor credenciais")
        decision = self._create_decision(
            category=IntentCategory.LOCAL_TASK,
            risk_labels=["destructive", "credentials", "private"],
        )

        safety_decision = self.policy.evaluate(decision, request)

        assert safety_decision.status == SafetyStatus.BLOCK
        assert safety_decision.reason_code == "destructive_operation"

    def test_case_insensitive_patterns(self):
        """Testar que padrões são case-insensitive."""
        request = self._create_request("RM -RF /tmp")
        decision = self._create_decision()

        safety_decision = self.policy.evaluate(decision, request)

        assert safety_decision.status == SafetyStatus.BLOCK

    def test_partial_pattern_match(self):
        """Testar que padrões encontram substring."""
        request = self._create_request("mostrar senha do banco")
        decision = self._create_decision()

        safety_decision = self.policy.evaluate(decision, request)

        assert safety_decision.status == SafetyStatus.CONFIRM

    def test_empty_message(self):
        """Testar com mensagem vazia."""
        request = self._create_request("")
        decision = self._create_decision()

        safety_decision = self.policy.evaluate(decision, request)

        assert safety_decision.status == SafetyStatus.ALLOW

    def test_confidence_levels(self):
        """Testar que confiança não afeta decisão de segurança."""
        for confidence in [0.5, 0.8, 0.99]:
            request = self._create_request("rm -rf teste")
            decision = self._create_decision(category=IntentCategory.CHITCHAT, risk_labels=[])

            safety_decision = self.policy.evaluate(decision, request)

            assert safety_decision.status == SafetyStatus.BLOCK
