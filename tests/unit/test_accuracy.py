"""Tests for accuracy calculator."""

import pytest

from alfred.eval.accuracy import calculate_accuracy, evaluate_dataset
from alfred.models import IntentCategory


class TestAccuracyCalculator:
    """Testes para calculadora de acurácia."""

    def test_calculate_accuracy_perfect(self):
        """Testar acurácia perfeita."""
        predictions = [
            IntentCategory.CHITCHAT,
            IntentCategory.CLOUD_TASK,
            IntentCategory.LOCAL_TASK,
        ]
        targets = [
            IntentCategory.CHITCHAT,
            IntentCategory.CLOUD_TASK,
            IntentCategory.LOCAL_TASK,
        ]

        result = calculate_accuracy(predictions, targets)

        assert result["accuracy"] == 1.0
        assert result["correct"] == 3
        assert result["total"] == 3

    def test_calculate_accuracy_partial(self):
        """Testar acurácia parcial."""
        predictions = [
            IntentCategory.CHITCHAT,
            IntentCategory.CLOUD_TASK,
            IntentCategory.LOCAL_TASK,
        ]
        targets = [
            IntentCategory.CHITCHAT,
            IntentCategory.CHITCHAT,
            IntentCategory.LOCAL_TASK,
        ]

        result = calculate_accuracy(predictions, targets)

        assert result["accuracy"] == 2 / 3
        assert result["correct"] == 2
        assert result["total"] == 3

    def test_calculate_accuracy_empty(self):
        """Testar acurácia com lista vazia."""
        result = calculate_accuracy([], [])
        assert result["accuracy"] == 0.0
        assert result["correct"] == 0
        assert result["total"] == 0

    def test_calculate_accuracy_mismatch_length(self):
        """Testar acurácia com comprimentos diferentes."""
        predictions = [IntentCategory.CHITCHAT]
        targets = [
            IntentCategory.CHITCHAT,
            IntentCategory.CLOUD_TASK,
        ]

        with pytest.raises(ValueError, match="Length mismatch"):
            calculate_accuracy(predictions, targets)

    def test_calculate_accuracy_per_category(self):
        """Testar acurácia por categoria."""
        predictions = [
            IntentCategory.CHITCHAT,
            IntentCategory.CLOUD_TASK,
            IntentCategory.LOCAL_TASK,
        ]
        targets = [
            IntentCategory.CHITCHAT,
            IntentCategory.CLOUD_TASK,
            IntentCategory.LOCAL_TASK,
        ]

        result = calculate_accuracy(predictions, targets)

        assert "CHITCHAT" in result["per_category"]
        assert "CLOUD_TASK" in result["per_category"]
        assert "LOCAL_TASK" in result["per_category"]

        chitchat_stats = result["per_category"]["CHITCHAT"]
        assert chitchat_stats["total"] == 1
        assert chitchat_stats["correct"] == 1

    def test_evaluate_dataset(self):
        """Testar avaliação de dataset completo."""
        results = [
            {
                "predicted_category": IntentCategory.CHITCHAT,
                "expected_category": IntentCategory.CHITCHAT,
            },
            {
                "predicted_category": IntentCategory.CLOUD_TASK,
                "expected_category": IntentCategory.CLOUD_TASK,
            },
            {
                "predicted_category": IntentCategory.LOCAL_TASK,
                "expected_category": IntentCategory.CHITCHAT,
            },
        ]

        result = evaluate_dataset(results)

        assert result["accuracy"] == 2 / 3
        assert result["correct"] == 2
        assert result["total"] == 3

    def test_evaluate_dataset_string_categories(self):
        """Testar avaliação com categorias como strings."""
        results = [
            {"predicted_category": "CHITCHAT", "expected_category": "CHITCHAT"},
            {"predicted_category": "CLOUD_TASK", "expected_category": "CLOUD_TASK"},
        ]

        result = evaluate_dataset(results)

        assert result["accuracy"] == 1.0

    def test_evaluate_dataset_empty(self):
        """Testar avaliação com dataset vazio."""
        result = evaluate_dataset([])

        assert result["accuracy"] == 0.0
        assert result["correct"] == 0
        assert result["total"] == 0

    def test_evaluate_dataset_missing_fields(self):
        """Testar avaliação com campos faltantes."""
        results = [
            {"predicted_category": IntentCategory.CHITCHAT},
            {"expected_category": IntentCategory.CHITCHAT},
            {
                "predicted_category": IntentCategory.CLOUD_TASK,
                "expected_category": IntentCategory.CLOUD_TASK,
            },
        ]

        result = evaluate_dataset(results)

        assert result["total"] == 1
        assert result["correct"] == 1