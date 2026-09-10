"""Roteamento de intenção."""

from typing import Any


def __getattr__(name: str) -> Any:
    """Importação perezosa para evitar cargar langchain en modo offline."""
    if name == "HeuristicIntentRouter":
        from alfred.routing.heuristic_router import HeuristicIntentRouter

        return HeuristicIntentRouter
    if name in ("IntentRouterImpl", "create_intent_router"):
        from alfred.routing.intent_router import IntentRouterImpl, create_intent_router

        exports = {
            "IntentRouterImpl": IntentRouterImpl,
            "create_intent_router": create_intent_router,
        }
        return exports[name]
    raise AttributeError(f"module 'alfred.routing' has no attribute {name!r}")


__all__ = ["HeuristicIntentRouter", "IntentRouterImpl", "create_intent_router"]
