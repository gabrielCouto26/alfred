"""Armazenamento local de memória efêmera de sessão."""

import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from platformdirs import user_data_dir

from alfred.contracts import SessionStore
from alfred.models import SessionContext, SessionStoreConfig, SessionTurn


class LocalSessionStore(SessionStore):
    """Implementação de SessionStore usando arquivo local com TTL."""

    def __init__(self, config: SessionStoreConfig | None = None):
        self._config = config or SessionStoreConfig()
        self._lock = threading.Lock()
        self._app_dir = Path(user_data_dir("alfred", "Alfred"))
        self._storage_path = Path(self._config.storage_path or self._app_dir)
        self._storage_path.mkdir(parents=True, exist_ok=True)

    def _get_session_path(self, session_id: str) -> Path:
        """Obter caminho do arquivo da sessão."""
        return self._storage_path / f"{session_id}.json"

    def load(self, session_id: str) -> SessionContext:
        """Carregar contexto de sessão do arquivo."""
        session_path = self._get_session_path(session_id)

        with self._lock:
            if not session_path.exists():
                return self._create_empty_context(session_id)

            try:
                with open(session_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                context = SessionContext(**data)

                if context.expires_at < datetime.now():
                    session_path.unlink(missing_ok=True)
                    return self._create_empty_context(session_id)

                return context
            except (json.JSONDecodeError, OSError):
                session_path.unlink(missing_ok=True)
                return self._create_empty_context(session_id)

    def append(self, session_id: str, turn: SessionTurn) -> None:
        """Adicionar turno à sessão e persistir."""
        session_path = self._get_session_path(session_id)

        with self._lock:
            context = self.load(session_id)
            context.turns.append(turn)
            context.last_message_at = datetime.now()
            context.expires_at = datetime.now() + timedelta(seconds=self._config.ttl_seconds)

            if len(context.turns) > self._config.max_turns:
                context.turns = context.turns[-self._config.max_turns:]

            self._save_context(session_path, context)

    def prune_expired(self) -> None:
        """Remover todas as sessões expiradas."""
        with self._lock:
            now = datetime.now()

            for session_file in self._storage_path.glob("*.json"):
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    context = SessionContext(**data)

                    if context.expires_at < now:
                        session_file.unlink(missing_ok=True)
                except (json.JSONDecodeError, OSError):
                    session_file.unlink(missing_ok=True)

    def _create_empty_context(self, session_id: str) -> SessionContext:
        """Criar contexto vazio para nova sessão."""
        now = datetime.now()
        expires = now + timedelta(seconds=self._config.ttl_seconds)

        return SessionContext(
            session_id=session_id,
            turns=[],
            created_at=now,
            expires_at=expires,
            version="1.0",
        )

    def _save_context(self, path: Path, context: SessionContext) -> None:
        """Salvar contexto em arquivo."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(context.model_dump(), f, ensure_ascii=False, indent=2)
