
from types import SimpleNamespace

from evaluation.run_regression import (
    compare_case,
    comparison_to_dict,
)


def test_ai_evidence_and_reasoning_are_preserved():
    case = {
        "case_id": "R10",
        "company": "Strategy& / PwC",
        "role": "Transformations & Deals",
        "reviewed_reference": {
            "data_relevance": {
                "score": 0,
                "status": "reviewed",
                "rationale": "No explicit data mandate.",
            }
        },
    }

    ai_result = SimpleNamespace(
        score=2,
        confidence=0.86,
        evidence=["Strategic analysis is mentioned."],
        reasoning="Analysis was interpreted as data work.",
    )

    assessment = SimpleNamespace(
        data_relevance=ai_result,
    )

    # compare_case expects all seven criteria.
    # Restrict this test to the criterion being examined.
    from unittest.mock import patch

    with patch(
        "evaluation.run_regression.CRITERIA",
        ["data_relevance"],
    ):
        comparisons = compare_case(case, assessment)

    result = comparison_to_dict(comparisons[0])

    assert result["ai_evidence"] == [
        "Strategic analysis is mentioned."
    ]
    assert result["ai_reasoning"] == (
        "Analysis was interpreted as data work."
    )
    assert result["reference_rationale"] == (
        "No explicit data mandate."
    )
    assert result["difference"] == 2
    assert result["disagrees"] is True
