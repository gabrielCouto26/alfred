"""Testes unitários para política de segurança."""

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


@pytest.fixture
def safety_policy():
    """Fixture para política de segurança."""
    return DeterministicSafetyPolicy()


class TestDeterministicSafetyPolicy:
    """Testes para DeterministicSafetyPolicy."""

    class TestBlockRules:
        """Testes para regras de bloqueio."""

        def test_block_rm_rf_command(self, safety_policy):
            """Deve bloquear comando rm -rf."""
            request = AssistantRequest(
                message="rm -rf /tmp/teste",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.BLOCK
            assert result.reason_code == "blocked_dangerous_command"

        def test_block_sudo_command(self, safety_policy):
            """Deve bloquear comando sudo."""
            request = AssistantRequest(
                message="sudo apt update",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.BLOCK

        def test_block_chmod_777(self, safety_policy):
            """Deve bloquear chmod 777."""
            request = AssistantRequest(
                message="chmod 777 /var/www",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.BLOCK

    class TestDangerousCommands:
        """Testes para comandos perigosos que exigem confirmação."""

        def test_dangerous_rm_command(self, safety_policy):
            """Deve exigir confirmação para comando rm."""
            request = AssistantRequest(
                message="rm arquivo.txt",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.CONFIRM
            assert result.reason_code == "dangerous_command_detected"

        def test_dangerous_mv_command(self, safety_policy):
            """Deve exigir confirmação para comando mv."""
            request = AssistantRequest(
                message="mv pasta1 pasta2",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.CONFIRM

        def test_dangerous_python_execution(self, safety_policy):
            """Deve exigir confirmação para execução python."""
            request = AssistantRequest(
                message="python script.py",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.CONFIRM

    class TestSensitiveOperations:
        """Testes para operações sensíveis que exigem confirmação."""

        def test_sensitive_database(self, safety_policy):
            """Deve exigir confirmação para operação com banco de dados."""
            request = AssistantRequest(
                message="apagar banco de dados antigo",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.CONFIRM
            assert "confirmação" in result.human_message.lower()

        def test_sensitive_password(self, safety_policy):
            """Deve exigir confirmação para operação com senha."""
            request = AssistantRequest(
                message="mostrar senha do sistema",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.CONFIRM

        def test_sensitive_financial(self, safety_policy):
            """Deve exigir confirmação para operação financeira."""
            request = AssistantRequest(
                message="transferir dinheiro para conta externa",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.CONFIRM

    class TestRiskLabels:
        """Testes para integração com risk_labels do IntentDecision."""

        def test_risk_destructive_blocks(self, safety_policy):
            """Deve bloquear com risk_label destructive."""
            request = AssistantRequest(
                message="qualquer coisa",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=["destructive"],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.BLOCK
            assert "destructive_operation" in result.reason_code

        def test_risk_credentials_blocks(self, safety_policy):
            """Deve bloquear com risk_label credentials."""
            request = AssistantRequest(
                message="mostrar credenciais",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=["credentials"],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.BLOCK

        def test_risk_private_confirms(self, safety_policy):
            """Deve exigir confirmação com risk_label private."""
            request = AssistantRequest(
                message="dados pessoais",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=["private"],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.CONFIRM

        def test_risk_financial_confirms(self, safety_policy):
            """Deve exigir confirmação com risk_label financial."""
            request = AssistantRequest(
                message="pagamento",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=["financial"],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.CONFIRM

        def test_risk_legal_confirms(self, safety_policy):
            """Deve exigir confirmação com risk_label legal."""
            request = AssistantRequest(
                message="contrato legal",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=["legal"],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.CONFIRM

        def test_risk_external_confirms(self, safety_policy):
            """Deve exigir confirmação com risk_label external."""
            request = AssistantRequest(
                message="integracao externa",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=["external"],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.CONFIRM

    class TestCategoryBased:
        """Testes para regras baseadas na categoria da intenção."""

        def test_blocked_category(self, safety_policy):
            """Deve bloquear se categoria for BLOCKED."""
            request = AssistantRequest(
                message="qualquer coisa",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.BLOCKED,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.BLOCK
            assert result.reason_code == "blocked_by_router"

        def test_out_of_scope_category(self, safety_policy):
            """Deve bloquear se categoria for OUT_OF_SCOPE."""
            request = AssistantRequest(
                message="qualquer coisa",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.OUT_OF_SCOPE,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.BLOCK
            assert result.reason_code == "out_of_scope"

    class TestAllow:
        """Testes para situações que devem ser permitidas."""

        def test_simple_chitchat_allowed(self, safety_policy):
            """Deve permitir saudação simples."""
            request = AssistantRequest(
                message="olá, como vai?",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.CHITCHAT,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.ALLOW
            assert result.reason_code == "no_risk_detected"

        def test_normal_task_allowed(self, safety_policy):
            """Deve permitir tarefa normal sem risco."""
            request = AssistantRequest(
                message="qual é a hora?",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.CLOUD_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert result.status == SafetyStatus.ALLOW

    class TestHumanMessages:
        """Testes para mensagens humanas."""

        def test_block_message_is_short(self, safety_policy):
            """Deve ter mensagem curta para bloqueio."""
            request = AssistantRequest(
                message="rm -rf /",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert len(result.human_message) < 100

        def test_confirm_message_is_short(self, safety_policy):
            """Deve ter mensagem curta para confirmação."""
            request = AssistantRequest(
                message="rm arquivo.txt",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.LOCAL_TASK,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert len(result.human_message) < 100

        def test_allow_message_is_short(self, safety_policy):
            """Deve ter mensagem curta para permitir."""
            request = AssistantRequest(
                message="olá",
                session_id="test-123",
                channel=Channel.CLI,
            )
            decision = IntentDecision(
                category=IntentCategory.CHITCHAT,
                confidence=0.95,
                rationale_code="test_rationale",
                required_clarification=None,
                simulated_tool_name=None,
                risk_labels=[],
            )

            result = safety_policy.evaluate(decision, request)

            assert len(result.human_message) < 100
