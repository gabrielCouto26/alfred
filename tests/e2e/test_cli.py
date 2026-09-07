"""Testes E2E para o módulo CLI."""

import subprocess
import sys
from pathlib import Path

import pytest


class TestCLIE2E:
    """Testes E2E da CLI."""
    
    @pytest.mark.e2e
    def test_cli_e2e_basic_flow(self, temp_app_dir):
        """Fluxo E2E básico da CLI."""
        result = subprocess.run(
            ["alfred", "Teste E2E básico"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 0
        assert "Alfred:" in result.stdout or "Recebi sua solicitação" in result.stdout
    
    @pytest.mark.e2e
    def test_cli_e2e_with_all_flags(self, temp_app_dir):
        """Fluxo E2E com todas as flags."""
        result = subprocess.run(
            [
                "alfred",
                "Teste com todas as flags",
                "--session", "e2e-full-test",
                "--json",
                "--no-trace"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 0
        assert result.stdout.strip()
