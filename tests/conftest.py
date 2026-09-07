"""Configuração pytest para o Alfred."""

import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_app_dir():
    """Fixture para diretório temporário de aplicação."""
    with tempfile.TemporaryDirectory() as tmpdir:
        app_dir = Path(tmpdir) / "alfred"
        app_dir.mkdir()
        yield app_dir


@pytest.fixture(autouse=True)
def clean_env():
    """Fixture para limpar variáveis de ambiente entre testes."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)
