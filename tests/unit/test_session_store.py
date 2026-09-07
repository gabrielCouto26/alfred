"""Testes unitários para memória de sessão."""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from alfred.memory import LocalSessionStore
from alfred.memory.session_store import LocalSessionStore as LocalSessionStoreImpl
from alfred.models import (
    IntentCategory,
    SessionContext,
    SessionStoreConfig,
    SessionTurn,
)


class TestLocalSessionStore:
    """Testes para LocalSessionStore."""

    def test_store_initialization_with_default_config(self, temp_app_dir):
        """Deve inicializar com configuração padrão."""
        config = SessionStoreConfig(storage_path=str(temp_app_dir))
        store = LocalSessionStore(config=config)

        assert store._config.storage_path == str(temp_app_dir)
        assert store._config.ttl_seconds == 7200
        assert store._config.max_turns == 10

    def test_store_initialization_with_custom_config(self, temp_app_dir):
        """Deve inicializar com configuração customizada."""
        config = SessionStoreConfig(
            ttl_seconds=3600, max_turns=5, storage_path=str(temp_app_dir)
        )
        store = LocalSessionStore(config=config)

        assert store._config.ttl_seconds == 3600
        assert store._config.max_turns == 5

    def test_load_nonexistent_session(self, temp_app_dir):
        """Deve retornar contexto vazio para sessão inexistente."""
        config = SessionStoreConfig(storage_path=str(temp_app_dir))
        store = LocalSessionStore(config=config)

        context = store.load("nonexistent-session")

        assert context.session_id == "nonexistent-session"
        assert context.turns == []
        assert context.version == "1.0"
        assert context.created_at is not None

    def test_append_and_load_turn(self, temp_app_dir):
        """Deve adicionar e recuperar turno corretamente."""
        config = SessionStoreConfig(storage_path=str(temp_app_dir))
        store = LocalSessionStore(config=config)

        now = datetime.now()
        expires = now + timedelta(hours=2)

        turn = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CHITCHAT,
            summary="Saudação inicial",
            decision_hash="abc123",
            category_label="Greeting",
            risk_labels=[],
        )

        store.append("test-session", turn)

        context = store.load("test-session")

        assert len(context.turns) == 1
        assert context.turns[0].summary == "Saudação inicial"
        assert context.turns[0].decision_hash == "abc123"
        assert context.session_id == "test-session"

    def test_append_multiple_turns(self, temp_app_dir):
        """Deve adicionar múltiplos turnos corretamente."""
        config = SessionStoreConfig(storage_path=str(temp_app_dir))
        store = LocalSessionStore(config=config)

        now = datetime.now()
        expires = now + timedelta(hours=2)

        for i in range(3):
            turn = SessionTurn(
                created_at=now,
                expires_at=expires,
                category=IntentCategory.CHITCHAT,
                summary=f"Saudação {i+1}",
                decision_hash=f"hash{i}",
                risk_labels=[],
            )
            store.append("multi-session", turn)

        context = store.load("multi-session")

        assert len(context.turns) == 3
        assert context.turns[0].summary == "Saudação 1"
        assert context.turns[2].summary == "Saudação 3"

    def test_turns_max_limit(self, temp_app_dir):
        """Deve respeitar limite máximo de turnos."""
        config = SessionStoreConfig(storage_path=str(temp_app_dir), max_turns=3)
        store = LocalSessionStore(config=config)

        now = datetime.now()
        expires = now + timedelta(hours=2)

        for i in range(5):
            turn = SessionTurn(
                created_at=now + timedelta(seconds=i),
                expires_at=expires,
                category=IntentCategory.CHITCHAT,
                summary=f"Mensagem {i+1}",
                decision_hash=f"hash{i}",
                risk_labels=[],
            )
            store.append("limit-session", turn)

        context = store.load("limit-session")

        assert len(context.turns) == 3
        assert context.turns[0].summary == "Mensagem 3"
        assert context.turns[2].summary == "Mensagem 5"

    def test_ttl_expiration(self, temp_app_dir):
        """Deve considerar sessão expirada após TTL."""
        config = SessionStoreConfig(
            storage_path=str(temp_app_dir), ttl_seconds=1, max_turns=10
        )
        store = LocalSessionStore(config=config)

        now = datetime.now()
        expires = now + timedelta(seconds=1)

        turn = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CHITCHAT,
            summary="Turno expirado",
            decision_hash="expired123",
            risk_labels=[],
        )

        store.append("expire-session", turn)
        time.sleep(1.5)

        context = store.load("expire-session")

        assert context.turns == []
        assert context.session_id == "expire-session"

    def test_persistence_file_created(self, temp_app_dir):
        """Deve criar arquivo de persistência."""
        config = SessionStoreConfig(storage_path=str(temp_app_dir))
        store = LocalSessionStore(config=config)

        now = datetime.now()
        expires = now + timedelta(hours=2)

        turn = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CHITCHAT,
            summary="Persistência test",
            decision_hash="persist123",
            risk_labels=[],
        )

        store.append("persist-session", turn)

        session_file = temp_app_dir / "persist-session.json"
        assert session_file.exists()

    def test_persistence_file_content(self, temp_app_dir):
        """Deve salvar conteúdo JSON válido."""
        config = SessionStoreConfig(storage_path=str(temp_app_dir))
        store = LocalSessionStore(config=config)

        now = datetime.now()
        expires = now + timedelta(hours=2)

        turn = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CHITCHAT,
            summary="Conteúdo test",
            decision_hash="content123",
            risk_labels=[],
        )

        store.append("content-session", turn)

        session_file = temp_app_dir / "content-session.json"
        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["session_id"] == "content-session"
        assert data["version"] == "1.0"
        assert len(data["turns"]) == 1
        assert data["turns"][0]["summary"] == "Conteúdo test"
        assert "message" not in data["turns"][0]

    def test_prune_expired_sessions(self, temp_app_dir):
        """Deve remover sessões expiradas."""
        config = SessionStoreConfig(
            storage_path=str(temp_app_dir), ttl_seconds=1, max_turns=10
        )
        store = LocalSessionStore(config=config)

        now = datetime.now()
        expires = now + timedelta(seconds=1)

        for i in range(3):
            turn = SessionTurn(
                created_at=now,
                expires_at=expires,
                category=IntentCategory.CHITCHAT,
                summary=f"Sessão {i}",
                decision_hash=f"prune{i}",
                risk_labels=[],
            )
            store.append(f"prune-session-{i}", turn)

        time.sleep(1.5)
        store.prune_expired()

        files = list(temp_app_dir.glob("*.json"))
        assert len(files) == 0

    def test_version_schema_persistence(self, temp_app_dir):
        """Deve persistir versão do schema."""
        config = SessionStoreConfig(storage_path=str(temp_app_dir))
        store = LocalSessionStore(config=config)

        now = datetime.now()
        expires = now + timedelta(hours=2)

        turn = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CHITCHAT,
            summary="Version test",
            decision_hash="version123",
            risk_labels=[],
        )

        store.append("version-session", turn)

        session_file = temp_app_dir / "version-session.json"
        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["version"] == "1.0"

    def test_no_raw_message_persistence(self, temp_app_dir):
        """Deve não persistir conteúdo bruto das mensagens."""
        config = SessionStoreConfig(storage_path=str(temp_app_dir))
        store = LocalSessionStore(config=config)

        now = datetime.now()
        expires = now + timedelta(hours=2)

        turn = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CHITCHAT,
            summary="Resumo da mensagem",
            decision_hash="rawtest123",
            risk_labels=[],
        )

        store.append("rawtest-session", turn)

        session_file = temp_app_dir / "rawtest-session.json"
        with open(session_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        turn_data = data["turns"][0]
        assert "message" not in turn_data
        assert "raw_message" not in turn_data
        assert "content" not in turn_data
