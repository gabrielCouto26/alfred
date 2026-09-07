"""Registry de tools simuladas para execução segura."""

from alfred.models import CloudTaskIntent, LocalTaskIntent, SimulatedToolResponse


class SimulatedToolsRegistry:
    """Registry de tools simuladas sem efeitos colaterais reais."""

    def simulate_cloud_task(self, task: CloudTaskIntent) -> SimulatedToolResponse:
        """Simular execução de tarefa em nuvem."""
        return SimulatedToolResponse(
            status="PREPARED",
            intention="simulated",
            requires_confirmation=True,
            human_message=f"Simulado: tarefa em nuvem '{task.task_name}'",
        )

    def simulate_local_task(self, task: LocalTaskIntent) -> SimulatedToolResponse:
        """Simular execução de tarefa local."""
        return SimulatedToolResponse(
            status="PREPARED",
            intention="simulated",
            requires_confirmation=True,
            human_message=f"Simulado: tarefa local '{task.task_name}'",
        )
