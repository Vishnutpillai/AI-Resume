from typing import Any

from app.schemas.matching import MatchResult


def _get_value(data: MatchResult | dict[str, Any], key: str) -> Any:
    """
    Safely retrieve a value from either a Pydantic model or dictionary.
    """
    if isinstance(data, dict):
        return data.get(key)

    return getattr(data, key, None)


def _get_breakdown(
    data: MatchResult | dict[str, Any],
) -> dict[str, float]:
    """
    Extract the score breakdown from a MatchResult or dictionary.
    """
    breakdown = _get_value(data, "breakdown")

    if breakdown is None:
        return {}

    if isinstance(breakdown, dict):
        return {
            key: float(value)
            for key, value in breakdown.items()
        }

    return {
        "required_skill_score": float(
            getattr(breakdown, "required_skill_score", 0.0)
        ),
        "semantic_score": float(
            getattr(breakdown, "semantic_score", 0.0)
        ),
        "experience_score": float(
            getattr(breakdown, "experience_score", 0.0)
        ),
        "project_score": float(
            getattr(breakdown, "project_score", 0.0)
        ),
        "education_score": float(
            getattr(breakdown, "education_score", 0.0)
        ),
        "preferred_skill_score": float(
            getattr(breakdown, "preferred_skill_score", 0.0)
        ),
    }


def compare_scores(
    before: MatchResult | dict[str, Any],
    after: MatchResult | dict[str, Any],
) -> dict[str, Any]:
    """
    Compare matching results before and after resume optimization.

    Returns:
        Overall score comparison, improvement, percentage improvement,
        improvement status, and component-level score changes.
    """

    before_score = float(_get_value(before, "overall_score") or 0.0)
    after_score = float(_get_value(after, "overall_score") or 0.0)

    absolute_improvement = after_score - before_score

    if before_score > 0:
        percentage_improvement = (
            absolute_improvement / before_score
        ) * 100
    else:
        percentage_improvement = 0.0

    before_breakdown = _get_breakdown(before)
    after_breakdown = _get_breakdown(after)

    component_deltas = {}

    all_components = set(before_breakdown) | set(after_breakdown)

    for component in sorted(all_components):
        before_value = before_breakdown.get(component, 0.0)
        after_value = after_breakdown.get(component, 0.0)

        component_deltas[component] = round(
            after_value - before_value,
            2,
        )

    return {
        "before_score": round(before_score, 2),
        "after_score": round(after_score, 2),
        "absolute_improvement": round(
            absolute_improvement,
            2,
        ),
        "percentage_improvement": round(
            percentage_improvement,
            2,
        ),
        "improved": after_score > before_score,
        "component_deltas": component_deltas,
    }