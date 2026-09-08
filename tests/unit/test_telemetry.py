"""Testes unitários para camada de observabilidade."""

import os
from unittest.mock import MagicMock, patch

from alfred.observability.telemetry import (
    TelemetryClient,
    create_event,
)


class TestTelemetryEvent:
    """Testes para TelemetryEvent."""

    def test_create_event_with_minimal_params(self):
        """Criar evento com parâmetros mínimos."""
        event = create_event(
            event_type="test_event",
            session_id="session-123",
            intent_category="CHITCHAT",
            safety_status="ALLOW",
            decision_hash="abc123",
            trace_id="trace456",
        )

        assert event.event_type == "test_event"
        assert event.session_id == "session-123"
        assert event.intent_category == "CHITCHAT"
        assert event.safety_status == "ALLOW"
        assert event.decision_hash == "abc123"
        assert event.trace_id == "trace456"
        assert event.timestamp is not None

    def test_create_event_with_optional_params(self):
        """Criar evento com parâmetros opcionais."""
        event = create_event(
            event_type="test_event",
            session_id="session-123",
            intent_category="CLOUD_TASK",
            safety_status="CONFIRM",
            decision_hash="def456",
            trace_id="trace789",
            intent_confidence=0.95,
            latency_ms=50.5,
            llm_model="gpt-4",
        )

        assert event.intent_confidence == 0.95
        assert event.latency_ms == 50.5
        assert event.llm_model == "gpt-4"


class TestTelemetryClient:
    """Testes para TelemetryClient."""

    def test_client_initialization(self):
        """Testar inicialização do cliente."""
        client = TelemetryClient(enabled=True, disable_content_tracing=True)
        assert client._enabled is True
        assert client._disable_content_tracing is True

    def test_client_disabled(self):
        """Testar cliente desabilitado."""
        client = TelemetryClient(enabled=False)
        assert client._enabled is False

    def test_generate_trace_id(self):
        """Testar geração de trace ID."""
        client = TelemetryClient()
        trace_id = client.generate_trace_id()
        assert len(trace_id) == 16
        assert isinstance(trace_id, str)

    def test_build_decision_hash(self):
        """Testar construção de hash de decisão."""
        client = TelemetryClient()
        decision_hash = client._build_decision_hash("CHITCHAT", 0.95, "greeting")
        assert len(decision_hash) == 16
        assert isinstance(decision_hash, str)

    def test_sanitize_message_disabled(self):
        """Testar sanitização com tracing desabilitado."""
        client = TelemetryClient(disable_content_tracing=True)
        result = client._sanitize_message("Senha secreta")
        assert result is None

    def test_sanitize_message_enabled(self):
        """Testar sanitização com tracing habilitado."""
        client = TelemetryClient(disable_content_tracing=False)
        result = client._sanitize_message("Mensagem segura")
        assert result == "Mensagem segura"

    def test_sanitize_message_none(self):
        """Testar sanitização com None."""
        client = TelemetryClient()
        result = client._sanitize_message(None)
        assert result is None

    @patch("logging.Logger.log")
    def test_emit_request(self, mock_logger):
        """Testar emissão de evento de requisição."""
        client = TelemetryClient()
        client.emit_request(session_id="test-sessao", trace_id="trace-123")

        assert mock_logger.called

    @patch("logging.Logger.log")
    def test_emit_classification(self, mock_logger):
        """Testar emissão de evento de classificação."""
        client = TelemetryClient()
        client.emit_classification(
            session_id="test-sessao",
            category="CHITCHAT",
            confidence=0.95,
            rationale_code="greeting_detected",
            trace_id="trace-123",
        )

        assert mock_logger.called

    @patch("logging.Logger.log")
    def test_emit_safety_check_block(self, mock_logger):
        """Testar emissão de evento de segurança com bloqueio."""
        client = TelemetryClient()
        client.emit_safety_check(
            session_id="test-sessao",
            category="LOCAL_TASK",
            safety_status="BLOCK",
            decision_hash="hash123",
            trace_id="trace-123",
        )

        assert mock_logger.called

    @patch("logging.Logger.log")
    def test_emit_safety_check_confirm(self, mock_logger):
        """Testar emissão de evento de segurança com confirmação."""
        client = TelemetryClient()
        client.emit_safety_check(
            session_id="test-sessao",
            category="CLOUD_TASK",
            safety_status="CONFIRM",
            decision_hash="hash456",
            trace_id="trace-123",
        )

        assert mock_logger.called

    @patch("logging.Logger.log")
    def test_emit_response(self, mock_logger):
        """Testar emissão de evento de resposta."""
        client = TelemetryClient()
        client.emit_response(
            session_id="test-sessao",
            category="CHITCHAT",
            safety_status="ALLOW",
            decision_hash="hash789",
            trace_id="trace-123",
        )

        assert mock_logger.called

    def test_trace_disabled(self):
        """Testar verificação de tracing desabilitado."""
        client = TelemetryClient(enabled=False)
        assert client.trace_disabled() is True

        client2 = TelemetryClient(disable_content_tracing=True)
        assert client2.trace_disabled() is True

    @patch("logging.Logger.log")
    def test_emit_ignored_when_disabled(self, mock_logger):
        """Testar que nenhún evento é emitido quando telemetry está desabilitada."""
        client = TelemetryClient(enabled=False)
        client.emit_request(session_id="test", trace_id="trace-1")
        client.emit_classification(
            session_id="test",
            category="CHITCHAT",
            confidence=0.9,
            rationale_code="greeting",
            trace_id="trace-1",
        )
        client.emit_safety_check(
            session_id="test",
            category="CHITCHAT",
            safety_status="ALLOW",
            decision_hash="hash",
            trace_id="trace-1",
        )
        client.emit_response(
            session_id="test",
            category="CHITCHAT",
            safety_status="ALLOW",
            decision_hash="hash",
            trace_id="trace-1",
        )

        assert not mock_logger.called

    @patch("logging.Logger.log")
    def test_langsmith_failure_degrades_gracefully(self, mock_logger):
        """Testar que falhas de LangSmith não interrompen o fluxo."""
        client = TelemetryClient()
        client._langsmith_client = MagicMock()
        client._langsmith_client.create_run.side_effect = Exception("network down")

        client.emit_request(session_id="test", trace_id="trace-1")

        assert client._langsmith_client is None
        assert mock_logger.called

    def test_emit_survives_after_langsmith_failure(self):
        """Testar que novos eventos seguem emitidos após falha de LangSmith."""
        client = TelemetryClient()
        failing = MagicMock()
        failing.create_run.side_effect = Exception("boom")
        client._langsmith_client = failing

        client.emit_request(session_id="test", trace_id="trace-1")
        client.emit_response(
            session_id="test",
            category="CHITCHAT",
            safety_status="ALLOW",
            decision_hash="hash",
            trace_id="trace-2",
        )

        assert client._langsmith_client is None

    def test_langsmith_not_configured_by_default(self):
        """Testar que LangSmith não se ativa sem configuração de ambiente."""
        client = TelemetryClient()
        assert client._langsmith_client is None


class TestTelemetryIntegration:
    """Testes de integração para telemetry."""

    def test_no_content_leak_in_logs(self, caplog):
        """Garantir que conteúdo bruto não vaze nos logs."""
        os.environ["ALFRED_DISABLE_CONTENT_TRACING"] = "true"
        client = TelemetryClient()

        client.emit_classification(
            session_id="test-session",
            category="CHITCHAT",
            confidence=0.95,
            rationale_code="greeting",
            trace_id="trace-123",
        )

        for record in caplog.records:
            assert "Olá" not in record.getMessage()
            assert "Senha" not in record.getMessage()

    def test_metrics_naming_convention(self):
        """Testar que métricas seguem convenção de nomenclatura."""
        event = create_event(
            event_type="alfred_request",
            session_id="test",
            intent_category="CHITCHAT",
            safety_status="ALLOW",
            decision_hash="hash",
            trace_id="trace",
        )

        assert event.event_type.startswith("alfred_")
        assert "request" in event.event_type
