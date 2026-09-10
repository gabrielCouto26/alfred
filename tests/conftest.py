"""Configuración pytest para Alfred."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def temp_app_dir():
    """Fixture para directorio temporal de aplicación."""
    with tempfile.TemporaryDirectory() as tmpdir:
        app_dir = Path(tmpdir) / "alfred"
        app_dir.mkdir()
        yield app_dir


@pytest.fixture(autouse=True)
def clean_env():
    """Fixture para limpiar variables de entorno entre tests."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def run_cli(tmp_path):
    """Ejecutar la CLI en un proceso real con entorno aislado.

    Usa el router heurístico offline y un directorio de datos temporal,
    de modo que no se requiere red, LLM ni OPENROUTER_API_KEY.
    """

    data_dir = tmp_path / "alfred-data"
    data_dir.mkdir(exist_ok=True)

    def _run(
        args: list[str],
        *,
        env_extra: dict[str, str] | None = None,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env["ALFRED_ROUTER"] = "heuristic"
        env["ALFRED_DATA_DIR"] = str(data_dir)
        if env_extra:
            env.update(env_extra)

        return subprocess.run(
            [sys.executable, "-m", "alfred", *args],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env=env,
            input=input_text,
        )

    return _run
