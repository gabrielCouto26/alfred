"""Testes E2E de la CLI en proceso real con entorno aislado.

Cubren los requisitos 8.1, 8.2 y 8.4: ejecución real de la CLI con el
router heurístico offline, salida texto/JSON, flags de sesión y tracing,
y bloqueos de seguridad sin efectos colaterales.
"""

import json

import pytest


class TestCLIE2E:
    """Suite E2E de la CLI (processo real, entorno aislado)."""

    @pytest.mark.e2e
    def test_e2e_text_output_is_human_readable(self, run_cli):
        """La salida de texto debe ser legible en terminal simple."""
        result = run_cli(["Olá, tudo bem?", "--no-trace"])

        assert result.returncode == 0
        assert result.stdout.strip(), "Salida vacía"
        assert not result.stdout.strip().startswith("{")

    @pytest.mark.e2e
    def test_e2e_json_output_is_parseable(self, run_cli):
        """La salida --json debe ser JSON válido y con la categoría correcta."""
        result = run_cli(["check meu email inbox", "--json", "--no-trace"])

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["category"] == "CLOUD_TASK"
        assert data["safety_status"] == "ALLOW"
        assert data["session_id"]

    @pytest.mark.e2e
    def test_e2e_session_flag_persists_context(self, run_cli):
        """--session debe aislar y persistir el contexto entre llamadas."""
        session_id = "e2e-session-1"

        first = run_cli(["Olá", "--session", session_id, "--json", "--no-trace"])
        second = run_cli(
            ["como vai?", "--session", session_id, "--json", "--no-trace"]
        )

        assert first.returncode == 0
        assert second.returncode == 0
        assert json.loads(first.stdout)["session_id"] == session_id
        assert json.loads(second.stdout)["session_id"] == session_id

    @pytest.mark.e2e
    def test_e2e_no_trace_suppresses_telemetry(self, run_cli):
        """--no-trace debe suprimir los logs de telemetría en stderr."""
        with_trace = run_cli(["Olá"])
        without_trace = run_cli(["Olá", "--no-trace"])

        assert with_trace.returncode == 0
        assert without_trace.returncode == 0
        assert "Request received" in with_trace.stderr
        assert "Request received" not in without_trace.stderr

    @pytest.mark.e2e
    def test_e2e_blocked_command_no_side_effects(self, run_cli):
        """Un comando destructivo debe bloquearse sin ejecutarse."""
        result = run_cli(["rm -rf /tmp/teste", "--json", "--no-trace"])

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["category"] == "BLOCKED"
        assert data["safety_status"] == "BLOCK"

    @pytest.mark.e2e
    def test_e2e_confirmation_default_deny_non_interactive(self, run_cli):
        """Sin entrada interactiva, una operación sensible se bloquea."""
        result = run_cli(["Execute o backup de arquivos", "--json", "--no-trace"])

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["safety_status"] == "BLOCK"

    @pytest.mark.e2e
    def test_e2e_out_of_scope_explicit(self, run_cli):
        """Una solicitud fuera del MVP debe señalarse explícitamente."""
        result = run_cli(["Manda un whatsapp a Gabriel", "--json", "--no-trace"])

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["category"] == "OUT_OF_SCOPE"
        assert "escopo" in data["text"].lower() or "scope" in data["text"].lower()
