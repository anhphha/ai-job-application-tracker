from types import SimpleNamespace

from criteria import CAREER_CRITERIA
from evaluation.run_regression import (
    calculate_metrics,
    calculate_reference_score,
    compare_case,
    CRITERIA,
    load_dataset,
    validate_dataset,
    dataset_reference_summary,
    CriterionComparison,
    comparison_to_dict,
)



def make_assessment():
    return SimpleNamespace(
        **{
            criterion: SimpleNamespace(score=1, confidence=0.9)
            for criterion in CAREER_CRITERIA
        }
    )


def make_case(reviewed_reference):
    return {
        "case_id": "R01",
        "company": "Example",
        "role": "Analyst",
        "reviewed_reference": reviewed_reference,
    }


def test_compare_case_skips_missing_reference_scores():
    comparisons = compare_case(make_case({}), make_assessment())

    assert comparisons == []
    assert calculate_metrics(comparisons)["total_reviewed"] == 0
    assert calculate_reference_score(make_case({})) is None


def test_compare_case_uses_reviewed_numeric_score():
    case = make_case(
        {
            "transformation": {
                "status": "reviewed",
                "score": 2,
                "rationale": "Clear transformation ownership.",
            }
        }
    )

    comparisons = compare_case(case, make_assessment())

    assert len(comparisons) == 1
    assert comparisons[0].reference_score == 2
    assert comparisons[0].reference_status == "reviewed"
    assert comparisons[0].difference == -1


def test_regression_dataset_is_valid():
    dataset = load_dataset()

    validate_dataset(dataset)

    reviewed, needs_review = (
        dataset_reference_summary(dataset)
    )

    assert len(dataset["cases"]) == 10
    assert reviewed == 70
    assert needs_review == 0


def test_regression_reference_scores_v1_2():
    dataset = load_dataset()

    assert dataset["dataset_version"] == "1.2"
    assert dataset["rubric_version"] == "2.1"

    expected = {
        "R01": {
            "transformation": 2,
            "business_ownership": 1,
            "stakeholder_exposure": 2,
            "data_relevance": 2,
            "decision_influence": 1,
            "change_adoption": 1,
            "leadership_potential": 1,
        },
        "R02": {
            "transformation": 1,
            "business_ownership": 1,
            "stakeholder_exposure": 1,
            "data_relevance": 2,
            "decision_influence": 1,
            "change_adoption": 0,
            "leadership_potential": 0,
        },
        "R03": {
            "transformation": 1,
            "business_ownership": 1,
            "stakeholder_exposure": 1,
            "data_relevance": 2,
            "decision_influence": 1,
            "change_adoption": 0,
            "leadership_potential": 0,
        },
        "R04": {
            "transformation": 1,
            "business_ownership": 1,
            "stakeholder_exposure": 1,
            "data_relevance": 1,
            "decision_influence": 1,
            "change_adoption": 1,
            "leadership_potential": 0,
        },
        "R05": {
            "transformation": 1,
            "business_ownership": 1,
            "stakeholder_exposure": 0,
            "data_relevance": 2,
            "decision_influence": 1,
            "change_adoption": 0,
            "leadership_potential": 0,
        },
        "R06": {
            "transformation": 2,
            "business_ownership": 1,
            "stakeholder_exposure": 1,
            "data_relevance": 2,
            "decision_influence": 1,
            "change_adoption": 0,
            "leadership_potential": 0,
        },
        "R07": {
            "transformation": 2,
            "business_ownership": 1,
            "stakeholder_exposure": 2,
            "data_relevance": 2,
            "decision_influence": 1,
            "change_adoption": 1,
            "leadership_potential": 1,
        },
        "R08": {
            "transformation": 2,
            "business_ownership": 1,
            "stakeholder_exposure": 1,
            "data_relevance": 2,
            "decision_influence": 2,
            "change_adoption": 2,
            "leadership_potential": 2,
        },
        "R09": {
            "transformation": 2,
            "business_ownership": 2,
            "stakeholder_exposure": 2,
            "data_relevance": 2,
            "decision_influence": 2,
            "change_adoption": 2,
            "leadership_potential": 2,
        },
        "R10": {
            "transformation": 2,
            "business_ownership": 2,
            "stakeholder_exposure": 1,
            "data_relevance": 0,
            "decision_influence": 2,
            "change_adoption": 1,
            "leadership_potential": 2,
        },
    }

    assert len(expected) == 10

    for case in dataset["cases"]:
        case_id = case["case_id"]

        assert case_id in expected

        actual = {
            criterion: case["reviewed_reference"][criterion]["score"]
            for criterion in CRITERIA
        }

        assert actual == expected[case_id]


def test_comparison_serialization():
    comparison = CriterionComparison(
        case_id="R01",
        company="Test Company",
        role="Test Role",
        criterion="business_ownership",
        ai_score=2,
        reference_score=1,
        confidence=0.9,
        reference_status="reviewed",
        reference_rationale="Test rationale.",
    )

    result = comparison_to_dict(
        comparison
    )

    assert result["difference"] == 1
    assert result["disagrees"] is True
    assert result["ai_score"] == 2
    assert result["reference_score"] == 1


def test_regression_metrics():
    comparisons = [
        CriterionComparison(
            case_id="R01",
            company="A",
            role="Role",
            criterion="transformation",
            ai_score=2,
            reference_score=2,
            confidence=0.9,
            reference_status="reviewed",
            reference_rationale="Test.",
        ),
        CriterionComparison(
            case_id="R01",
            company="A",
            role="Role",
            criterion="business_ownership",
            ai_score=2,
            reference_score=1,
            confidence=0.9,
            reference_status="reviewed",
            reference_rationale="Test.",
        ),
    ]

    metrics = calculate_metrics(
        comparisons
    )

    assert metrics["reviewed_criteria"] == 2
    assert metrics["agreements"] == 1
    assert metrics["disagreements"] == 1
    assert metrics["ai_higher"] == 1
    assert metrics["ai_lower"] == 0
    assert metrics["agreement_rate"] == 0.5
    assert (
        metrics["mean_absolute_difference"]
        == 0.5
    )


def test_needs_review_excluded_from_primary_metrics():
    comparisons = [
        CriterionComparison(
            case_id="R01",
            company="A",
            role="Role",
            criterion="transformation",
            ai_score=0,
            reference_score=2,
            confidence=0.99,
            reference_status="needs_review",
            reference_rationale="Boundary case.",
        )
    ]

    metrics = calculate_metrics(
        comparisons
    )

    assert metrics["reviewed_criteria"] == 0
    assert metrics["agreements"] == 0
    assert metrics["disagreements"] == 0
    assert metrics["ai_higher"] == 0
    assert metrics["ai_lower"] == 0