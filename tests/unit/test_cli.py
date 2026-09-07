"""Testes unitários para o módulo CLI."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


class TestCLIArgumentParsing:
    """Testes de parsing de argumentos da CLI."""
    
    @pytest.mark.unit
    def test_cli_requires_message(self, temp_app_dir):
        """A CLI deve requerer mensagem como argumento."""
        result = subprocess.run(
            ["alfred"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 1
        assert "mensagem é obrigatória" in result.stderr.lower()
    
    @pytest.mark.unit
    def test_cli_accepts_session_flag(self, temp_app_dir):
        """A CLI deve aceitar flag --session."""
        result = subprocess.run(
            [
                "alfred",
                "test message",
                "--session", "test-session"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 0
        assert "test message" in result.stdout or result.returncode == 0
    
    @pytest.mark.unit
    def test_cli_accepts_json_flag(self, temp_app_dir):
        """A CLI deve aceitar flag --json."""
        result = subprocess.run(
            [
                "alfred",
                "test message",
                "--json"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 0
        try:
            json.loads(result.stdout)
            assert True
        except json.JSONDecodeError:
            assert False, "Saída não é JSON válido"
    
    @pytest.mark.unit
    def test_cli_accepts_no_trace_flag(self, temp_app_dir):
        """A CLI deve aceitar flag --no-trace."""
        result = subprocess.run(
            [
                "alfred",
                "test message",
                "--no-trace"
            ],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 0
    
    @pytest.mark.unit
    def test_cli_invalid_input_returns_error_code(self, temp_app_dir):
        """CLI deve retornar código de erro para entradas inválidas."""
        result = subprocess.run(
            ["alfred"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 1


class TestCLIOutputFormats:
    """Testes de formatos de saída da CLI."""
    
    @pytest.mark.unit
    def test_cli_text_output_is_human_readable(self, temp_app_dir):
        """Saída em texto deve ser legível."""
        result = subprocess.run(
            ["alfred", "test message"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 0
        assert result.stdout.strip()
        assert not result.stdout.startswith("{")
    
    @pytest.mark.unit
    def test_cli_json_output_is_valid_json(self, temp_app_dir):
        """Saída em JSON deve ser válida."""
        result = subprocess.run(
            ["alfred", "test message", "--json"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent.parent)
        )
        
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, dict)
        assert "text" in data or "error" in data
