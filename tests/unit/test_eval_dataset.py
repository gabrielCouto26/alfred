"""Tests for eval dataset."""

from alfred.models import IntentCategory
from tests.fixtures.eval_cases import EVAL_CASES


class TestEvalDataset:
    """Testes para dataset de avaliação."""

    def test_dataset_not_empty(self):
        """Testar que dataset não está vazio."""
        assert len(EVAL_CASES) > 0

    def test_dataset_structure(self):
        """Testar estrutura de casos do dataset."""
        for case in EVAL_CASES:
            assert "id" in case
            assert "message" in case
            assert "expected_category" in case
            assert "confidence_threshold" in case
            assert "rationale" in case

    def test_all_categories_represented(self):
        """Testar que todas as categorias estão representadas."""
        categories = {case["expected_category"] for case in EVAL_CASES}
        expected_categories = {cat for cat in IntentCategory}

        assert categories.issubset(expected_categories)

    def test_confidence_thresholds_valid(self):
        """Testar que thresholds de confiança são válidos."""
        for case in EVAL_CASES:
            assert 0.0 <= case["confidence_threshold"] <= 1.0

    def test_rationales_not_empty(self):
        """Testar que todas as justificativas não estão vazias."""
        for case in EVAL_CASES:
            assert len(case["rationale"]) > 0