"""Módulo de observabilidade."""

from alfred.observability.telemetry import (
    TelemetryClient,
    TelemetryEvent,
    create_event,
    get_telemetry_client,
)

__all__ = ["TelemetryClient", "TelemetryEvent", "create_event", "get_telemetry_client"]
