import json
from pathlib import Path

CRITERIA = (
    "transformation",
    "business_ownership",
    "stakeholder_exposure",
    "data_relevance",
    "decision_influence",
    "change_adoption",
    "leadership_potential",
)

path = Path("evaluation/candidate_references_1_1.json")
dataset = json.loads(path.read_text(encoding="utf-8"))

assert dataset["dataset_version"] == "1.1-rc1"
assert dataset["rubric_version"] == "2.0"

cases = dataset["cases"]
assert len(cases) == 10
assert len({case["case_id"] for case in cases}) == 10

pending = []

for case in cases:
    reference = case.get("reviewed_reference")

    # R01–R05: preserve original Dataset 1.0 references.
    if reference is None:
        assert case["case_id"] in {
            "R01", "R02", "R03", "R04", "R05"
        }
        continue

    assert set(reference) == set(CRITERIA)

    for criterion, item in reference.items():
        assert item["score"] in (0,1,2)
        assert item["status"] in ("reviewed", "needs_review")
        assert item["rationale"].strip()

        if item["status"] == "needs_review":
            pending.append((case["case_id"], criterion))

print(f"Cases: {len(cases)}")
print(f"Pending reviews: {len(pending)}")

for case_id, criterion in pending:
    print(f"  {case_id}: {criterion}")

