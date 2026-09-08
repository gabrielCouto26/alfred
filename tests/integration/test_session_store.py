"""Testes de integração para memória de sessão."""

import time
from datetime import datetime, timedelta

from alfred.memory import LocalSessionStore
from alfred.models import IntentCategory, SessionStoreConfig, SessionTurn


class TestSessionStoreIntegration:
    """Testes de integração para LocalSessionStore."""

    def test_session_state_preserved_across_loads(self, temp_app_dir):
        """Deve preservar estado da sessão entre chamadas load."""
        config = SessionStoreConfig(storage_path=str(temp_app_dir))
        store = LocalSessionStore(config=config)

        session_id = "integration-test-session"

        now = datetime.now()
        expires = now + timedelta(hours=2)

        turn1 = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CHITCHAT,
            summary="Primeira mensagem",
            decision_hash="turn1",
            risk_labels=[],
        )
        store.append(session_id, turn1)

        context = store.load(session_id)
        assert len(context.turns) == 1

        turn2 = SessionTurn(
            created_at=now + timedelta(seconds=1),
            expires_at=expires,
            category=IntentCategory.LOCAL_TASK,
            summary="Segunda mensagem",
            decision_hash="turn2",
            risk_labels=[],
        )
        store.append(session_id, turn2)

        context = store.load(session_id)
        assert len(context.turns) == 2
        assert context.turns[0].summary == "Primeira mensagem"
        assert context.turns[1].summary == "Segunda mensagem"

    def test_concurrent_access(self, temp_app_dir):
        """Deve ser thread-safe para acesso concorrente."""
        config = SessionStoreConfig(
            storage_path=str(temp_app_dir), max_turns=50
        )
        store = LocalSessionStore(config=config)

        session_id = "concurrent-test"
        num_threads = 5
        turns_per_thread = 3

        def add_turns(thread_id: int):
            now = datetime.now()
            expires = now + timedelta(hours=2)

            for i in range(turns_per_thread):
                turn = SessionTurn(
                    created_at=now + timedelta(seconds=i),
                    expires_at=expires,
                    category=IntentCategory.CHITCHAT,
                    summary=f"Thread {thread_id} - Turno {i}",
                    decision_hash=f"thread{thread_id}_turn{i}",
                    risk_labels=[],
                )
                store.append(session_id, turn)

        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(add_turns, i) for i in range(num_threads)]
            for future in futures:
                future.result()

        context = store.load(session_id)

        expected_turns = num_threads * turns_per_thread
        assert len(context.turns) == expected_turns

    def test_empty_session_after_prune(self, temp_app_dir):
        """Deve criar nova sessão vazia após prune de sessão existente."""
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
            decision_hash="prune123",
            risk_labels=[],
        )
        store.append("prune-test", turn)

        time.sleep(1.5)
        store.prune_expired()

        context = store.load("prune-test")

        assert context.session_id == "prune-test"
        assert context.turns == []
        assert context.version == "1.0"

    def test_multiple_sessions_independent(self, temp_app_dir):
        """Deve manter sessões independentes uma da outra."""
        config = SessionStoreConfig(storage_path=str(temp_app_dir))
        store = LocalSessionStore(config=config)

        now = datetime.now()
        expires = now + timedelta(hours=2)

        for i in range(3):
            session_id = f"independent-session-{i}"

            turn = SessionTurn(
                created_at=now,
                expires_at=expires,
                category=IntentCategory.CHITCHAT,
                summary=f"Mensagem {i}",
                decision_hash=f"ind{i}",
                risk_labels=[],
            )
            store.append(session_id, turn)

        for i in range(3):
            session_id = f"independent-session-{i}"
            context = store.load(session_id)

            assert len(context.turns) == 1
            assert context.turns[0].summary == f"Mensagem {i}"

    def test_expires_at_updates_on_append(self, temp_app_dir):
        """Deve atualizar expires_at a cada append."""
        config = SessionStoreConfig(
            storage_path=str(temp_app_dir), ttl_seconds=3600, max_turns=10
        )
        store = LocalSessionStore(config=config)

        session_id = "expires-update-test"
        now = datetime.now()
        expires = now + timedelta(seconds=1)

        turn1 = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CHITCHAT,
            summary="Primeira mensagem",
            decision_hash="expires1",
            risk_labels=[],
        )
        store.append(session_id, turn1)

        context1 = store.load(session_id)
        first_expires = context1.expires_at

        time.sleep(0.1)

        turn2 = SessionTurn(
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=1),
            category=IntentCategory.CHITCHAT,
            summary="Segunda mensagem",
            decision_hash="expires2",
            risk_labels=[],
        )
        store.append(session_id, turn2)

        context2 = store.load(session_id)
        second_expires = context2.expires_at

        assert second_expires > first_expires

    def test_storage_directory_creation(self, temp_app_dir):
        """Deve criar diretório de armazenamento se não existir."""
        nested_path = temp_app_dir / "nested" / "deep" / "path"
        config = SessionStoreConfig(storage_path=str(nested_path))
        store = LocalSessionStore(config=config)

        now = datetime.now()
        expires = now + timedelta(hours=2)

        turn = SessionTurn(
            created_at=now,
            expires_at=expires,
            category=IntentCategory.CHITCHAT,
            summary="Nested test",
            decision_hash="nested123",
            risk_labels=[],
        )

        store.append("nested-session", turn)

        session_file = nested_path / "nested-session.json"
        assert session_file.exists()

        context = store.load("nested-session")
        assert context.session_id == "nested-session"

    def test_large_number_of_turns(self, temp_app_dir):
        """Deve lidar com número grande de turnos (respeitando max_turns)."""
        config = SessionStoreConfig(
            storage_path=str(temp_app_dir), ttl_seconds=3600, max_turns=50
        )
        store = LocalSessionStore(config=config)

        session_id = "large-turns-test"
        now = datetime.now()
        expires = now + timedelta(hours=2)

        for i in range(100):
            turn = SessionTurn(
                created_at=now + timedelta(seconds=i),
                expires_at=expires,
                category=IntentCategory.CHITCHAT,
                summary=f"Mensagem {i}",
                decision_hash=f"large{i}",
                risk_labels=[],
            )
            store.append(session_id, turn)

        context = store.load(session_id)

        assert len(context.turns) == 50
        assert context.turns[0].summary == "Mensagem 50"
        assert context.turns[49].summary == "Mensagem 99"
