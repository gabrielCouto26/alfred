"""Calculadora de acurácia para dataset de avaliação."""

from typing import Any

from alfred.models import IntentCategory


def calculate_accuracy(
    predictions: list[IntentCategory],
    targets: list[IntentCategory],
) -> dict[str, Any]:
    """Calcular acurácia entre previsões e alvos."""
    if len(predictions) != len(targets):
        raise ValueError(
            f"Length mismatch: {len(predictions)} predictions vs {len(targets)} targets"
        )

    if not predictions:
        return {
            "accuracy": 0.0,
            "correct": 0,
            "total": 0,
            "per_category": {},
        }

    correct = sum(
        1 for pred, target in zip(predictions, targets) if pred == target
    )
    accuracy = correct / len(predictions)

    per_category: dict[str, dict[str, int]] = {}
    for category in IntentCategory:
        cat_str = category.value
        per_category[cat_str] = {"correct": 0, "total": 0}

    for pred, target in zip(predictions, targets):
        target_str = target.value

        per_category[target_str]["total"] += 1
        if pred == target:
            per_category[target_str]["correct"] += 1

    for cat_str in per_category:
        total = per_category[cat_str]["total"]
        if total > 0:
            per_category[cat_str]["accuracy"] = (
                per_category[cat_str]["correct"] / total
            )
        else:
            per_category[cat_str]["accuracy"] = 0.0

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": len(predictions),
        "per_category": per_category,
    }


def evaluate_dataset(
    results: list[dict[str, Any]],
    target_category_field: str = "predicted_category",
    expected_category_field: str = "expected_category",
) -> dict[str, Any]:
    """Avaliar resultado completo do dataset."""
    predictions = []
    targets = []

    for item in results:
        pred = item.get(target_category_field)
        target = item.get(expected_category_field)

        if pred is None or target is None:
            continue

        if isinstance(pred, str):
            pred = IntentCategory(pred)
        if isinstance(target, str):
            target = IntentCategory(target)

        predictions.append(pred)
        targets.append(target)

    return calculate_accuracy(predictions, targets)
