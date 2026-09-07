"""Tests for intent router."""

import pytest
from unittest.mock import MagicMock, patch

from alfred.models import IntentCategory, IntentDecision, SessionContext, SessionTurn
from alfred.routing.intent_router import create_intent_router


@pytest.fixture
def router():
    """Fixture para router com mock do LLM."""
    with patch("alfred.routing.intent_router.create_llm_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        router = create_intent_router()
        router.llm_client = mock_client
        return router


class TestIntentRouter:
    """Testes para IntentRouter."""

    def test_classify_chitchat_greeting(self, router):
        """Testar classificação de saudação."""
        from alfred.models import AssistantRequest, Channel

        mock_response = IntentDecision(
            category=IntentCategory.CHITCHAT,
            confidence=0.95,
            rationale_code="greeting_detected",
        )
        router.llm_client.generate.return_value = mock_response

        request = AssistantRequest(
            message="Olá, tudo bem?",
            session_id="test-session",
            channel=Channel.CLI,
        )

        result = router.classify(request)

        assert result.category == IntentCategory.CHITCHAT
        assert result.confidence >= 0.9
        assert result.rationale_code == "greeting_detected"

    def test_classify_cloud_task(self, router):
        """Testar classificação de tarefa em nuvem."""
        from alfred.models import AssistantRequest, Channel

        mock_response = IntentDecision(
            category=IntentCategory.CLOUD_TASK,
            confidence=0.88,
            rationale_code="cloud_service",
        )
        router.llm_client.generate.return_value = mock_response

        request = AssistantRequest(
            message="Check meu email inbox",
            session_id="test-session",
            channel=Channel.CLI,
        )

        result = router.classify(request)

        assert result.category == IntentCategory.CLOUD_TASK
        assert result.confidence >= 0.8

    def test_classify_local_task(self, router):
        """Testar classificação de tarefa local."""
        from alfred.models import AssistantRequest, Channel

        mock_response = IntentDecision(
            category=IntentCategory.LOCAL_TASK,
            confidence=0.92,
            rationale_code="local_execution",
        )
        router.llm_client.generate.return_value = mock_response

        request = AssistantRequest(
            message="Execute o script backup.sh",
            session_id="test-session",
            channel=Channel.CLI,
        )

        result = router.classify(request)

        assert result.category == IntentCategory.LOCAL_TASK

    def test_classify_ambiguous(self, router):
        """Testar classificação ambígua."""
        from alfred.models import AssistantRequest, Channel

        mock_response = IntentDecision(
            category=IntentCategory.AMBIGUOUS,
            confidence=0.65,
            rationale_code="insufficient_context",
        )
        router.llm_client.generate.return_value = mock_response

        request = AssistantRequest(
            message="Açao",
            session_id="test-session",
            channel=Channel.CLI,
        )

        result = router.classify(request)

        assert result.category == IntentCategory.AMBIGUOUS

    def test_classify_with_session_context(self, router):
        """Testar classificação com contexto de sessão."""
        from datetime import datetime, timedelta

        from alfred.models import AssistantRequest, Channel

        now = datetime.now()
        context = SessionContext(
            session_id="test-session",
            turns=[
                SessionTurn(
                    created_at=now,
                    expires_at=now + timedelta(hours=2),
                    category=IntentCategory.CHITCHAT,
                    summary="User greeted",
                    decision_hash="hash123",
                )
            ],
            created_at=now,
            expires_at=now + timedelta(hours=2),
        )

        mock_response = IntentDecision(
            category=IntentCategory.CHITCHAT,
            confidence=0.9,
            rationale_code="chitchat_pattern",
        )
        router.llm_client.generate.return_value = mock_response

        request = AssistantRequest(
            message="Como vai?",
            session_id="test-session",
            channel=Channel.CLI,
        )

        result = router.classify(request, context=context)

        assert result.category == IntentCategory.CHITCHAT

    def test_generate_rationale_code(self, router):
        """Testar geração de código de justificativa."""
        from alfred.models import AssistantRequest, Channel, IntentCategory

        request = AssistantRequest(
            message="Olá, tudo bem?",
            session_id="test-session",
            channel=Channel.CLI,
        )

        decision = IntentDecision(
            category=IntentCategory.CHITCHAT,
            confidence=0.95,
            rationale_code="",
        )

        result = router._post_process_decision(decision, request)

        assert result.rationale_code == "greeting_detected"

    def test_build_history(self, router):
        """Testar construção de histórico."""
        from datetime import datetime, timedelta

        now = datetime.now()
        context = SessionContext(
            session_id="test-session",
            turns=[
                SessionTurn(
                    created_at=now,
                    expires_at=now + timedelta(hours=2),
                    category=IntentCategory.CHITCHAT,
                    summary="User greeted",
                    decision_hash="hash123",
                )
            ],
            created_at=now,
            expires_at=now + timedelta(hours=2),
        )

        history = router._build_history(context, None)

        assert "CHITCHAT" in history
        assert "User greeted" in history

    def test_build_history_empty(self, router):
        """Testar construção de histórico vazio."""
        history = router._build_history(None, None)
        assert history == ""

    def test_invalid_llm_response(self, router):
        """Testar tratamento de resposta inválida do LLM."""
        router.llm_client.generate.return_value = "invalid response"

        from alfred.models import AssistantRequest, Channel

        request = AssistantRequest(
            message="Test",
            session_id="test-session",
            channel=Channel.CLI,
        )

        with pytest.raises(ValueError, match="Resposta LLM não é um IntentDecision"):
            router.classify(request)

    def test_classify_blocked(self, router):
        """Testar classificação bloqueada."""
        from alfred.models import AssistantRequest, Channel

        mock_response = IntentDecision(
            category=IntentCategory.BLOCKED,
            confidence=0.95,
            rationale_code="blocked_pattern",
        )
        router.llm_client.generate.return_value = mock_response

        request = AssistantRequest(
            message="Execute rm -rf /tmp/teste",
            session_id="test-session",
            channel=Channel.CLI,
        )

        result = router.classify(request)

        assert result.category == IntentCategory.BLOCKED

    def test_classify_out_of_scope(self, router):
        """Testar classificação fora de escopo."""
        from alfred.models import AssistantRequest, Channel

        mock_response = IntentDecision(
            category=IntentCategory.OUT_OF_SCOPE,
            confidence=0.9,
            rationale_code="out_of_scope_pattern",
        )
        router.llm_client.generate.return_value = mock_response

        request = AssistantRequest(
            message="Funcionalidade futura não implementada",
            session_id="test-session",
            channel=Channel.CLI,
        )

        result = router.classify(request)

        assert result.category == IntentCategory.OUT_OF_SCOPE