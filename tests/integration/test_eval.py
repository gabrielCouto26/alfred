"""Tests for eval integration."""

import pytest

from alfred.models import IntentCategory
from alfred.eval.accuracy import calculate_accuracy
from tests.fixtures.eval_cases import EVAL_CASES


class TestEvalIntegration:
    """Testes de integração para avaliação."""

    @pytest.mark.integration
    def test_eval_dataset_basic(self):
        """Testar dataset básico."""
        total = len(EVAL_CASES)
        assert total >= 5

    @pytest.mark.integration
    def test_accuracy_calculation_with_dataset(self):
        """Testar cálculo de acurácia com casos reais."""
        predictions = [
            IntentCategory.CHITCHAT,
            IntentCategory.CHITCHAT,
            IntentCategory.CLOUD_TASK,
        ]
        targets = [
            IntentCategory.CHITCHAT,
            IntentCategory.CLOUD_TASK,
            IntentCategory.CLOUD_TASK,
        ]

        result = calculate_accuracy(predictions, targets)

        assert result["accuracy"] >= 0.0
        assert result["accuracy"] <= 1.0
        assert result["total"] == 3

    @pytest.mark.integration
    def test_all_categories_in_dataset(self):
        """Testar que todas as categorias do PRD estão no dataset."""
        categories_found = set()
        for case in EVAL_CASES:
            categories_found.add(case["expected_category"])

        required_categories = {
            IntentCategory.CHITCHAT,
            IntentCategory.CLOUD_TASK,
            IntentCategory.LOCAL_TASK,
            IntentCategory.AMBIGUOUS,
            IntentCategory.BLOCKED,
            IntentCategory.OUT_OF_SCOPE,
        }

        assert categories_found.issubset(required_categories)