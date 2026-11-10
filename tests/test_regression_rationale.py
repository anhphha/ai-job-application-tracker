
from evaluation.run_regression import (
    CriterionComparison,
    comparison_to_dict,
)


def test_comparison_preserves_rationales():
    comparison = CriterionComparison(
        case_id="R10",
        company="Strategy& / PwC",
        role="Transformations & Deals",
        criterion="data_relevance",
        ai_score=2,
        reference_score=0,
        confidence=0.86,
        reference_status="reviewed",
        reference_rationale="No explicit data/AI mandate.",
        ai_rationale="Example AI explanation.",
        ai_evidence=["Evidence 1", "Evidence 2"],
        ai_reasoning="AI reasoning explanation.",
    )

    result = comparison_to_dict(comparison)

    assert result["ai_rationale"] == "Example AI explanation."
    assert result["reference_rationale"] == (
        "No explicit data/AI mandate."
    )
    assert result["ai_evidence"] == ["Evidence 1", "Evidence 2"]
    assert result["ai_reasoning"] == "AI reasoning explanation."
    assert result["difference"] == 2
    assert result["disagrees"] is True
