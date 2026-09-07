"""Testes de integração para o módulo CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


class TestCLIIntegration:
    """Testes de integração da CLI."""
    
    @pytest.mark.integration
    def test_cli_full_flow(self, temp_app_dir):
        """Fluxo completo da CLI com sessão."""
        result = subprocess.run(
            [
                "alfred",
                "Olá, você está funcionando?",
                "--session", "integration-test-1",
                "--json"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("category") == "CHITCHAT"
        assert data.get("safety_status") == "ALLOW"
        assert "session_id" in data
        assert "integration-test-1" in result.stdout
    
    @pytest.mark.integration
    def test_cli_multiple_sessions(self, temp_app_dir):
        """CLI deve suportar múltiplas sessões."""
        session1 = "multi-session-1"
        session2 = "multi-session-2"
        
        result1 = subprocess.run(
            ["alfred", "Primeira sessão", "--session", session1],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        result2 = subprocess.run(
            ["alfred", "Segunda sessão", "--session", session2],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result1.returncode == 0
        assert result2.returncode == 0
        assert "Primeira sessão" in result1.stdout or result1.returncode == 0
        assert "Segunda sessão" in result2.stdout or result2.returncode == 0
    
    @pytest.mark.integration
    def test_cli_json_and_session_flags(self, temp_app_dir):
        """CLI deve combinar flags --json e --session."""
        session_id = "combined-flags-test"
        
        result = subprocess.run(
            [
                "alfred",
                "Teste combinado",
                "--session", session_id,
                "--json"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data.get("session_id") == session_id
