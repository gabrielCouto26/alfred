"""Testes de integración de la CLI (proceso real con entorno aislado)."""

import json

import pytest


class TestCLIIntegration:
    """Testes de integración de la CLI."""

    @pytest.mark.integration
    def test_cli_full_flow(self, run_cli):
        """Flujo completo de la CLI con sesión."""
        result = run_cli(
            ["Olá, você está funcionando?", "--session", "integration-test-1", "--json"]
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("category") == "CHITCHAT"
        assert data.get("safety_status") == "ALLOW"
        assert data.get("session_id") == "integration-test-1"

    @pytest.mark.integration
    def test_cli_multiple_sessions(self, run_cli):
        """La CLI debe soportar múltiples sesiones aisladas."""
        first = run_cli(["Primeira sessão", "--session", "multi-1", "--no-trace"])
        second = run_cli(["Segunda sessão", "--session", "multi-2", "--no-trace"])

        assert first.returncode == 0
        assert second.returncode == 0
        assert first.stdout.strip()
        assert second.stdout.strip()

    @pytest.mark.integration
    def test_cli_json_and_session_flags(self, run_cli):
        """La CLI debe combinar flags --json y --session."""
        result = run_cli(
            ["Teste combinado", "--session", "combined-flags", "--json", "--no-trace"]
        )

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("session_id") == "combined-flags"

    @pytest.mark.integration
    def test_cli_error_without_message(self, run_cli):
        """Sin mensaje la CLI debe fallar con código de error."""
        result = run_cli([])

        assert result.returncode == 1
        assert "mensaje es obligatorio" in result.stderr.lower()

    @pytest.mark.integration
    def test_cli_config_error_without_key_and_llm_router(self, run_cli):
        """Sin OPENROUTER_API_KEY y con router LLM, error claro de configuración."""
        result = run_cli(
            ["hola", "--json", "--no-trace"],
            env_extra={"ALFRED_ROUTER": "llm"},
        )

        assert result.returncode == 2
        data = json.loads(result.stdout)
        assert data.get("error") == "INTERNAL_ERROR"
        assert "OPENROUTER_API_KEY" in data.get("message", "")
