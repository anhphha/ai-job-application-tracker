import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import json
import argparse
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from extractor import extract_job
from assessor import assess_job
from criteria_v2_1 import CAREER_CRITERIA, RUBRIC_VERSION
from assessor import (
    ASSESSMENT_PROMPT_VERSION as PROMPT_VERSION,
    MODEL_NAME,
)

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "regression_cases.json"
RESULTS_DIR = BASE_DIR / "results"


@dataclass
class CriterionComparison:
    case_id: str
    company: str
    role: str
    criterion: str
    ai_score: int
    reference_score: int
    confidence: float
    reference_status: str
    reference_rationale: str
    ai_evidence: list[str] = field(default_factory=list)
    ai_reasoning: str = ""
    ai_rationale: str = ""

    @property
    def difference(self)->int:
        return self.ai_score - self.reference_score

    @property
    def disagrees(self)->bool:
        return self.ai_score != self.reference_score

    @property
    def is_primary(self)->bool:
        return self.reference_status == "reviewed"


def load_dataset(path: Path | None = None) -> dict:
    dataset_path = path or DATASET_PATH
    with dataset_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_job_description(relative_path: str) -> str:
    path = BASE_DIR / relative_path

    if not path.exists():
        raise FileNotFoundError(f"Job description fixture not found: {path}"
    )

    return path.read_text(encoding="utf-8")


def evaluate_case(case:dict):
    job_description = load_job_description(
        case["job_description_file"]
    )

    extraction = extract_job(job_description)

    assessment = assess_job(
        job_description,
        extraction
    )

    return assessment


CRITERIA = [
    "transformation",
    "business_ownership",
    "stakeholder_exposure",
    "data_relevance",
    "decision_influence",
    "change_adoption",
    "leadership_potential",
]

def compare_case(
    case:dict,
    assessment,
)-> list[CriterionComparison]:

    comparisons = []
    reviewed_reference = case.get("reviewed_reference", {})

    for criterion in CRITERIA:
        reference = reviewed_reference.get(criterion)
        if reference is None:
            continue
        if reference.get("status") != "reviewed":
            continue
        if "score" not in reference:
            raise ValueError(
                f"Reviewed reference for {case['case_id']} "
                f"is missing a score for {criterion}"
            )

        ai_result = getattr(assessment,criterion)

        comparisons.append(
            CriterionComparison(
                case_id = case["case_id"],
                company = case["company"],
                role = case["role"],
                criterion = criterion,
                ai_score= ai_result.score,
                reference_score=reference["score"],
                confidence=ai_result.confidence,
                reference_status=reference["status"],
                reference_rationale=reference.get("rationale", ""),
                ai_evidence=list(getattr(ai_result, "evidence", [])),
                ai_reasoning=getattr(ai_result, "reasoning", ""),
                ai_rationale=getattr(ai_result, "reasoning", ""),
            )
        )

    return comparisons


def calculate_metrics(
    comparisons : list[CriterionComparison],
)-> dict:
    primary = [
        c for c in comparisons if c.is_primary
    ]

    disagreements = [
        c for c in primary if c.disagrees
    ]

    ai_higher = [
        c for c in disagreements if c.difference > 0
    ]

    ai_lower = [
        c for c in disagreements if c.difference < 0
    ]

    total_reviewed = len(primary)
    agreement_count = (
        total_reviewed - len(disagreements)
    )

    agreement_rate = (
        agreement_count / total_reviewed
        if total_reviewed
        else None
    )

    mean_absolute_difference = (
        sum(abs(c.difference) for c in primary)
        / total_reviewed
        if total_reviewed
        else None
    )

    high_confidence_disagreements = [
        c for c in disagreements
        if c.confidence >= HIGH_CONFIDENCE_THRESHOLD
    ]

    return {
        "total_reviewed": len(primary),
        "reviewed_criteria": len(primary),
        "agreements": len(primary) - len(disagreements),
        "disagreements" : len(disagreements),
        "agreement_rate": agreement_rate,
        "ai_higher": len(ai_higher),
        "ai_lower": len(ai_lower),
        "mean_absolute_difference": (
            mean_absolute_difference
        ),
        "high_confidence_disagreements": (
            len(high_confidence_disagreements)
        ),
    }


def criterion_summary(
    comparisons: list[CriterionComparison],
) -> dict:

    summary = {}


    for criterion in CRITERIA:

        rows = [
            c for c in comparisons
            if c.criterion == criterion and c.is_primary
        ]

        disagreements = [
            c for c in rows if c.disagrees
        ]

        disagreement_rate = (
            len(disagreements) / len(rows)
            if rows
            else 0.0
        )

        summary[criterion] = {
            "reviewed": len(rows),
            "disagreements": len(disagreements),
            "disagreement_rate": disagreement_rate,
            "ai_higher": sum(
                c.difference > 0
                for c in disagreements
            ),
            "ai_lower": sum(
                c.difference < 0
                for c in disagreements
            ),
        }

    return summary


HIGH_CONFIDENCE_THRESHOLD = 0.80

def high_confidence_disagreements(
    comparisons: list[CriterionComparison],
) -> list[CriterionComparison]:

    return [
        c for c in comparisons
        if c.is_primary
        and c.disagrees
        and c.confidence >= HIGH_CONFIDENCE_THRESHOLD
    ]


def calculate_reference_score(case:dict) -> Optional[float]:

    reference = case.get("reviewed_reference", {})

    if any(
        criterion not in reference
        or reference[criterion].get("status") != "reviewed"
        for criterion in CAREER_CRITERIA
    ):
        return None

    total = 0.0

    for criterion, config in CAREER_CRITERIA.items():
        score = reference[criterion]["score"]
        total += (score/2)* config["weight"]

    return round(total * 100, 1)


def print_summary(
    metrics: dict,
    summary: dict,
    high_confidence: list[CriterionComparison],
) -> None:
    print("\nRegression summary")
    print(f"Reviewed criteria: {metrics['total_reviewed']}")

    if metrics["total_reviewed"] == 0:
        print(
            "No reviewed reference scores are present; "
            "agreement metrics are unavailable."
        )
    else:
        print(f"Agreements: {metrics['agreements']}")
        print(f"Disagreements: {metrics['disagreements']}")
        print(f"AI scored higher: {metrics['ai_higher']}")
        print(f"AI scored lower: {metrics['ai_lower']}")

    print("\nPer-criterion results")
    for criterion, values in summary.items():
        print(
            f"{criterion}: {values['reviewed']} reviewed, "
            f"{values['disagreements']} disagreements"
        )

    print(
        "\nHigh-confidence disagreements "
        f"(confidence >= {HIGH_CONFIDENCE_THRESHOLD:.0%}): "
        f"{len(high_confidence)}"
    )
    for comparison in high_confidence:
        print(
            f"- {comparison.case_id} {comparison.criterion}: "
            f"AI {comparison.ai_score}, reference "
            f"{comparison.reference_score} "
            f"(confidence {comparison.confidence:.0%})"
        )

def validate_dataset(dataset:dict)->None:
    cases = dataset.get("cases", [])

    if not cases:
        raise ValueError(
            "Regression dataset contains no cases."
        )

    validate_statuses = {
        "reviewed",
        "needs_review",
    }

    for case in cases:
        case_id = case.get("case_id", "<unknown>")
        reference = case.get("reviewed_reference")

        if not reference:
            raise ValueError(
                f"{case_id}: reviewed_reference is missing or empty."
            )

        for criterion in CRITERIA:
            if criterion not in reference:
                raise ValueError(
                    f"{case_id}: missing reviewed reference "
                    f"for '{criterion}'"
                )

            item = reference[criterion]

            if "score" not in item:
                raise ValueError(
                    f"{case_id}/{criterion}: missing score."
                )

            if item["score"] not in {0,1,2}:
                raise ValueError(
                    f"{case_id}/{criterion}: "
                    f"score must be 0, 1, or 2."
                )

            status = item.get("status")

            if status not in validate_statuses:
                raise ValueError(
                    f"{case_id}/{criterion}: "
                    f"invalid status '{status}'."
                )

            if not item.get("rationale"):
                raise ValueError(
                    f"{case_id}/{criterion}: "
                    f"review rationale is missing."
                )


def dataset_reference_summary(dataset: dict) -> tuple[int, int]:
    reviewed = 0
    needs_review = 0

    for case in dataset["cases"]:
        reference = case["reviewed_reference"]

        for criterion in CRITERIA:
            status = reference[criterion]["status"]

            if status == "reviewed":
                reviewed += 1
            elif status == "needs_review":
                needs_review += 1

    return reviewed, needs_review

def print_reference_scores(dataset: dict) -> None:
    print("\nReviewed reference scores")

    for case in dataset["cases"]:
        scores = {
            criterion: case["reviewed_reference"][criterion]["score"]
            for criterion in CRITERIA
        }

        print(f"{case['case_id']}: {scores}")

def print_all_disagreements(
    comparisons: list[CriterionComparison],
) -> None:

    disagreements = [
        c for c in comparisons
        if c.is_primary and c.disagrees
    ]

    print("\nAll disagreements")

    if not disagreements:
        print("None")
        return

    for c in disagreements:
        direction = (
            "AI higher"
            if c.difference > 0
            else "AI lower"
        )

        print(
            f"- {c.case_id} {c.criterion}: "
            f"AI {c.ai_score}, "
            f"reference {c.reference_score}, "
            f"confidence {c.confidence:.0%}, "
            f"{direction}"
        )

def mean_absolute_difference(
    comparisons: list[CriterionComparison],
) -> float:
    primary = [
        c for c in comparisons
        if c.is_primary
    ]

    if not primary:
        return 0.0

    return sum(
        abs(c.difference)
        for c in primary
    ) / len(primary)



def create_experiment_id(dataset_version: str) -> str:
    timestamp = datetime.now(timezone.utc)

    safe_version = dataset_version.replace(".", "_")

    return (
        f"regression_v{safe_version}_"
        f"{timestamp.strftime('%Y%m%dT%H%M%S_%fZ')}"
    )



def comparison_to_dict(
    comparison: CriterionComparison,
) -> dict:
    return {
        "case_id": comparison.case_id,
        "company": comparison.company,
        "role": comparison.role,
        "criterion": comparison.criterion,
        "ai_score": comparison.ai_score,
        "ai_rationale": comparison.ai_rationale,
        "ai_evidence": comparison.ai_evidence,
        "ai_reasoning": comparison.ai_reasoning,
        "reference_rationale": comparison.reference_rationale,
        "reference_score": comparison.reference_score,
        "difference": comparison.difference,
        "confidence": comparison.confidence,
        "reference_status": comparison.reference_status,
        "disagrees": comparison.disagrees,
    }


def build_experiment_record(
    dataset: dict,
    comparisons: list[CriterionComparison],
) -> dict:

    metrics = calculate_metrics(comparisons)
    criterion_metrics = criterion_summary(comparisons)

    experiment_id = create_experiment_id(
    dataset_version=dataset["dataset_version"]
    )

    return {
        "experiment": {
            "experiment_id": experiment_id,
            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "dataset_version": dataset[
                "dataset_version"
            ],
            "rubric_version": RUBRIC_VERSION,
            "prompt_version": PROMPT_VERSION,
            "model": MODEL_NAME,
            "high_confidence_threshold": (
                HIGH_CONFIDENCE_THRESHOLD
            ),
        },
        "summary": metrics,
        "criterion_summary": criterion_metrics,
        "results": [
            comparison_to_dict(c)
            for c in comparisons
        ],
    }



def save_experiment_record(record: dict) -> Path:
    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    experiment_id = record["experiment"]["experiment_id"]

    final_path = RESULTS_DIR / f"{experiment_id}.json"

    # "x" = exclusive creation:
    # Create a new file only if it does not already exist.
    # If the file exists, raise FileExistsError.
    with final_path.open("x", encoding="utf-8") as f:
        json.dump(
            record,
            f,
            indent=2,
            ensure_ascii=False,
        )

    return final_path



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DATASET_PATH,
        help="Path to regression dataset JSON",
    )
    args = parser.parse_args()

    dataset = load_dataset(args.dataset)

    validate_dataset(dataset)

    reviewed_count, needs_review_count = (dataset_reference_summary(dataset))

    print(f"Dataset version: {dataset['dataset_version']}")
    print(f"Cases: {len(dataset['cases'])}")
    print(f"Reviewed references: {reviewed_count}")
    print(f"Needs review: {needs_review_count}")

    print_reference_scores(dataset)

    all_comparisons = []

    print(
        f"Dataset version: "
        f"{dataset['dataset_version']}"
    )

    for case in dataset["cases"]:
        print(
            f"\nEvaluating {case['case_id']} - "
            f"{case['company']} / {case['role']}"
        )

        assessment = evaluate_case(case)

        comparisons = compare_case(
            case,
            assessment,
        )

        all_comparisons.extend(comparisons)


    metrics = calculate_metrics(all_comparisons)

    summary = criterion_summary(all_comparisons)

    high_confidence = (
        high_confidence_disagreements(all_comparisons)
    )

    print_summary(
        metrics,
        summary,
        high_confidence
    )

    print_all_disagreements(all_comparisons)


    record = build_experiment_record(
        dataset,
        all_comparisons,
    )

    result_path = save_experiment_record(
        record
    )

    print(
        f"\nExperiment saved: {result_path}"
    )


if __name__ == "__main__":
    main()