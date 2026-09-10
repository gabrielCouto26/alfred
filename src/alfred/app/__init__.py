"""Módulo de aplicación del Alfred."""

import os

from alfred.tools.simulated_registry import SimulatedToolsRegistry

from .assistant_service import AssistantServiceImpl


def create_assistant_service() -> AssistantServiceImpl:
    """Factory para crear una instancia del AssistantService.

    - ``ALFRED_ROUTER=heuristic`` usa un router determinístico offline
      (sin LLM ni red), útil para tests E2E y validación local.
    - ``ALFRED_DATA_DIR`` aísla el directorio de persistencia de sesiones.
    """
    from alfred.contracts import IntentRouter
    from alfred.memory.session_store import LocalSessionStore, SessionStoreConfig
    from alfred.routing.heuristic_router import HeuristicIntentRouter
    from alfred.safety.policy import DeterministicSafetyPolicy

    router_mode = os.getenv("ALFRED_ROUTER", "llm").lower()
    if router_mode == "heuristic":
        intent_router: IntentRouter = HeuristicIntentRouter()
    else:
        from alfred.routing.intent_router import IntentRouterImpl

        intent_router = IntentRouterImpl()

    safety_policy = DeterministicSafetyPolicy()
    storage_path = os.getenv("ALFRED_DATA_DIR")
    session_store = LocalSessionStore(SessionStoreConfig(storage_path=storage_path))
    simulated_registry = SimulatedToolsRegistry()

    return AssistantServiceImpl(
        intent_router=intent_router,
        safety_policy=safety_policy,
        session_store=session_store,
        simulated_tools_registry=simulated_registry,
    )


__all__ = [
    "AssistantServiceImpl",
    "SimulatedToolsRegistry",
    "create_assistant_service",
]
