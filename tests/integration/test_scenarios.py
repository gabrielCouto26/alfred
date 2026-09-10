"""Cenarios de integração representativos de los requisitos funcionales del PRD.

Cubren el flujo CLI completo (processo real) con router heurístico offline
para chitchat, cloud task, local task, ambigüedad, bloqueo, confirmación y
fuera de alcance (requisito 8.3).
"""

import json

import pytest

from alfred.eval.accuracy import evaluate_dataset
from alfred.routing.heuristic_router import HeuristicIntentRouter
from tests.fixtures.eval_cases import EVAL_CASES


class TestPRDScenariosCLI:
    """Escenarios funcionales del PRD a través de la CLI real."""

    @pytest.mark.integration
    def test_scenario_chitchat(self, run_cli):
        """RF-1/RF-2: conversación rápida sin tools."""
        result = run_cli(["Olá, tudo bem?", "--json", "--no-trace"])

        data = json.loads(result.stdout)
        assert data["category"] == "CHITCHAT"
        assert data["safety_status"] == "ALLOW"
        assert data["text"].strip()

    @pytest.mark.integration
    def test_scenario_cloud_task(self, run_cli):
        """RF-9: tarea en la nube se prepara de forma simulada."""
        result = run_cli(["Agende evento na agenda do Google", "--json", "--no-trace"])

        data = json.loads(result.stdout)
        assert data["category"] == "CLOUD_TASK"
        assert "Simulado" in data["text"]
        assert data["metadata"]["tool_status"] == "PREPARED"

    @pytest.mark.integration
    def test_scenario_local_task(self, run_cli):
        """RF-9: tarea local se prepara de forma simulada, sin ejecución."""
        result = run_cli(
            ["Liste os arquivos da pasta projetos", "--json", "--no-trace"]
        )

        data = json.loads(result.stdout)
        assert data["category"] == "LOCAL_TASK"
        assert "Simulado" in data["text"]

    @pytest.mark.integration
    def test_scenario_ambiguous_asks_clarification(self, run_cli):
        """RF-11: solicitud ambigua pide clarificación."""
        result = run_cli(["Açao", "--json", "--no-trace"])

        data = json.loads(result.stdout)
        assert data["category"] == "AMBIGUOUS"
        assert data["text"].strip()

    @pytest.mark.integration
    def test_scenario_blocked_explains_why(self, run_cli):
        """RF-16/RF-17: bloqueo con explicación breve."""
        result = run_cli(["rm -rf /tmp/teste", "--json", "--no-trace"])

        data = json.loads(result.stdout)
        assert data["category"] == "BLOCKED"
        assert data["safety_status"] == "BLOCK"
        assert data["text"].strip()

    @pytest.mark.integration
    def test_scenario_confirmation_required(self, run_cli):
        """RF-15: operación sensible exige confirmación (denegada sin stdin)."""
        result = run_cli(["Execute o backup de arquivos", "--json", "--no-trace"])

        data = json.loads(result.stdout)
        assert data["safety_status"] == "BLOCK"

    @pytest.mark.integration
    def test_scenario_out_of_scope_signaled(self, run_cli):
        """RF-12: capacidad fuera del alcance se señala sin falsa expectativa."""
        result = run_cli(["Manda un whatsapp a Gabriel", "--json", "--no-trace"])

        data = json.loads(result.stdout)
        assert data["category"] == "OUT_OF_SCOPE"

    @pytest.mark.integration
    def test_scenario_no_real_automation_executed(self, run_cli, tmp_path):
        """Ninguna automatización real debe ejecutarse (solo simulación)."""
        marker = tmp_path / "ejecutado.sh"
        result = run_cli(
            ["Execute o script de backup.sh", "--json", "--no-trace"],
            env_extra={"ALFRED_PHANTOM_SCRIPT": str(marker)},
        )

        assert result.returncode == 0
        assert not marker.exists(), "Se ejecutó un script real"

    @pytest.mark.integration
    def test_scenario_ambiguous_and_out_of_scope_are_distinct(self, run_cli):
        """RF-18: distinguir 'no puedo', 'aún no en alcance' e 'insuficiente'."""
        ambiguous = json.loads(run_cli(["Açao", "--json", "--no-trace"]).stdout)
        out_of_scope = json.loads(
            run_cli(["Manda un whatsapp", "--json", "--no-trace"]).stdout
        )

        assert ambiguous["category"] == "AMBIGUOUS"
        assert out_of_scope["category"] == "OUT_OF_SCOPE"


class TestHeuristicRouterEval:
    """Baseline offline de acurácia sobre el dataset de evaluación."""

    @pytest.mark.integration
    def test_heuristic_router_reaches_accuracy_target(self):
        """El router heurístico debe superar el 85% de acurácia del PRD."""
        router = HeuristicIntentRouter()
        from alfred.models import AssistantRequest

        results = []
        for case in EVAL_CASES:
            request = AssistantRequest(
                message=case["message"],
                session_id=f"eval-{case['id']}",
                channel="cli",
            )
            decision = router.classify(request)
            results.append(
                {
                    "predicted_category": decision.category,
                    "expected_category": case["expected_category"],
                }
            )

        metrics = evaluate_dataset(results)
        assert metrics["accuracy"] >= 0.85, metrics
