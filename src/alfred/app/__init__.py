"""Módulo de aplicação do Alfred."""

from alfred.tools.simulated_registry import SimulatedToolsRegistry

from .assistant_service import AssistantServiceImpl


def create_assistant_service() -> AssistantServiceImpl:
    """Factory para criar instância do AssistantService com dependências padrão."""
    from alfred.llm.openrouter_client import create_llm_client
    from alfred.memory.session_store import LocalSessionStore, SessionStoreConfig
    from alfred.routing.intent_router import IntentRouterImpl
    from alfred.safety.policy import DeterministicSafetyPolicy

    intent_router = IntentRouterImpl()
    safety_policy = DeterministicSafetyPolicy()
    session_store = LocalSessionStore(SessionStoreConfig())
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
