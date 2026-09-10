"""Testes unitários de la CLI (parsing de argumentos y renderizado)."""

import json
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from alfred.cli import app
from alfred.exit_codes import EXIT_INPUT_ERROR, EXIT_INTERNAL_ERROR, EXIT_SUCCESS
from alfred.models import (
    AssistantResponse,
    IntentCategory,
    SafetyStatus,
)


@pytest.fixture
def cli_runner(monkeypatch):
    """Runner con servicio mockeado para pruebas unitarias."""

    mock_service = MagicMock()
    mock_service.handle.return_value = AssistantResponse(
        text="Respuesta de prueba",
        category=IntentCategory.CHITCHAT,
        safety_status=SafetyStatus.ALLOW,
        session_id="default-cli-session",
        metadata={"rationale_code": "test"},
    )
    monkeypatch.setattr(
        "alfred.cli.create_assistant_service", lambda: mock_service
    )
    return CliRunner(), mock_service


class TestCLIArgumentParsing:
    """Testes de parsing de argumentos."""

    @pytest.mark.unit
    def test_cli_requires_message(self, cli_runner):
        runner, _ = cli_runner
        result = runner.invoke(app, [])

        assert result.exit_code == EXIT_INPUT_ERROR
        assert "mensaje es obligatorio" in result.stderr.lower()

    @pytest.mark.unit
    def test_cli_requires_message_json(self, cli_runner):
        runner, _ = cli_runner
        result = runner.invoke(app, ["--json"])

        assert result.exit_code == EXIT_INPUT_ERROR
        data = json.loads(result.stdout)
        assert data["error"] == "INPUT_ERROR"

    @pytest.mark.unit
    def test_cli_accepts_session_flag(self, cli_runner):
        runner, mock_service = cli_runner
        result = runner.invoke(app, ["hola", "--session", "unit-session"])

        assert result.exit_code == EXIT_SUCCESS
        assert result.stdout.strip() == "Respuesta de prueba"

    @pytest.mark.unit
    def test_cli_passes_session_id(self, cli_runner):
        runner, mock_service = cli_runner
        result = runner.invoke(app, ["hola", "--session", "unit-session"])

        assert result.exit_code == EXIT_SUCCESS
        request = mock_service.handle.call_args[0][0]
        assert request.session_id == "unit-session"

    @pytest.mark.unit
    def test_cli_accepts_json_flag(self, cli_runner):
        runner, mock_service = cli_runner
        result = runner.invoke(app, ["hola", "--json"])

        assert result.exit_code == EXIT_SUCCESS
        data = json.loads(result.stdout)
        assert data["text"] == "Respuesta de prueba"
        assert data["category"] == "CHITCHAT"

    @pytest.mark.unit
    def test_cli_accepts_no_trace_flag(self, cli_runner):
        runner, mock_service = cli_runner
        result = runner.invoke(app, ["hola", "--no-trace"])

        assert result.exit_code == EXIT_SUCCESS
        request = mock_service.handle.call_args[0][0]
        assert request.trace_enabled is False

    @pytest.mark.unit
    def test_cli_trace_enabled_by_default(self, cli_runner):
        runner, mock_service = cli_runner
        result = runner.invoke(app, ["hola"])

        assert result.exit_code == EXIT_SUCCESS
        request = mock_service.handle.call_args[0][0]
        assert request.trace_enabled is True

    @pytest.mark.unit
    def test_cli_internal_error_exit_code(self, cli_runner, monkeypatch):
        runner, mock_service = cli_runner
        mock_service.handle.side_effect = RuntimeError("boom")
        monkeypatch.setattr(
            "alfred.cli.create_assistant_service", lambda: mock_service
        )

        result = runner.invoke(app, ["hola"])

        assert result.exit_code == EXIT_INTERNAL_ERROR
        assert "Error interno" in result.stderr


class TestCLIOutputFormats:
    """Testes de formatos de salida."""

    @pytest.mark.unit
    def test_cli_text_output_is_human_readable(self, cli_runner):
        runner, _ = cli_runner
        result = runner.invoke(app, ["hola"])

        assert result.exit_code == EXIT_SUCCESS
        assert result.stdout.strip()
        assert not result.stdout.strip().startswith("{")

    @pytest.mark.unit
    def test_cli_json_output_is_valid_json(self, cli_runner):
        runner, _ = cli_runner
        result = runner.invoke(app, ["hola", "--json"])

        assert result.exit_code == EXIT_SUCCESS
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert "text" in data
