import sys
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import database
from database import (
    initialize_database,
    get_all_jobs,
    get_job_assessments,
    get_job_overrides,
    get_effective_assessment_scores,
    get_job_ai_runs,
    get_evaluation_summary,
)
from models import AIRunMetadata, CriterionAssessment, JobAssessment, JobExtraction
from workflow import HumanOverride, JobReview, ReviewStatus


initialize_database()

jobs = get_all_jobs()

for job in jobs:
    print(job)

assessments = get_job_assessments(
    job_id=1
)

for assessment in assessments:
    print(assessment)

overrides = get_job_overrides(
    job_id=1
)

for override in overrides:
    print(override)


class DatabaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_database_name = database.DATABASE_NAME
        database.DATABASE_NAME = str(Path(self.temp_dir.name) / "test.db")
        database.initialize_database()

    def get_all_jobs(self) -> list[JobReview]:
        jobs = get_all_jobs()
        job_reviews = []

        for job in jobs:
            assessment = JobAssessment(
                transformation=CriterionAssessment(
                    score=job["transformation_score"],
                    evidence=json.loads(job["transformation_evidence"]),
                    reasoning=job["transformation_reasoning"],
                    confidence=job["transformation_confidence"],
                ),
                business_ownership=CriterionAssessment(
                    score=job["business_ownership_score"],
                    evidence=json.loads(job["business_ownership_evidence"]),
                    reasoning=job["business_ownership_reasoning"],
                    confidence=job["business_ownership_confidence"],
                ),
                stakeholder_exposure=CriterionAssessment(
                    score=job["stakeholder_exposure_score"],
                    evidence=json.loads(job["stakeholder_exposure_evidence"]),
                    reasoning=job["stakeholder_exposure_reasoning"],
                    confidence=job["stakeholder_exposure_confidence"],
                ),
                data_relevance=CriterionAssessment(
                    score=job["data_relevance_score"],
                    evidence=json.loads(job["data_relevance_evidence"]),
                    reasoning=job["data_relevance_reasoning"],
                    confidence=job["data_relevance_confidence"],
                ),
                decision_influence=CriterionAssessment(
                    score=job["decision_influence_score"],
                    evidence=json.loads(job["decision_influence_evidence"]),
                    reasoning=job["decision_influence_reasoning"],
                    confidence=job["decision_influence_confidence"],
                ),
                change_adoption=CriterionAssessment(
                    score=job["change_adoption_score"],
                    evidence=json.loads(job["change_adoption_evidence"]),
                    reasoning=job["change_adoption_reasoning"],
                    confidence=job["change_adoption_confidence"],
                ),
                leadership_potential=CriterionAssessment(
                    score=job["leadership_potential_score"],
                    evidence=json.loads(job["leadership_potential_evidence"]),
                    reasoning=job["leadership_potential_reasoning"],
                    confidence=job["leadership_potential_confidence"],
                ),
            )

            job_review = JobReview(
                job=JobExtraction(
                    company=job.get("company"),
                    role=job.get("role"),
                    location=job.get("location"),
                ),
                assessment=assessment,
                career_score=job.get("career_score", 0.0),
                status=ReviewStatus(job.get("status", "pending")),
            )
            job_reviews.append(job_review)

        return job_reviews


    def tearDown(self) -> None:
        database.DATABASE_NAME = self.original_database_name
        self.temp_dir.cleanup()

    def test_save_approved_job_serializes_evidence_as_json(self) -> None:
        assessment = JobAssessment(**{
            criterion: CriterionAssessment(
                score=1,
                evidence=["First piece of evidence", "Second piece"],
                reasoning="Supported by the description",
                confidence=0.8,
            )
            for criterion in (
                "transformation",
                "business_ownership",
                "stakeholder_exposure",
                "data_relevance",
                "decision_influence",
                "change_adoption",
                "leadership_potential",
            )
        })
        review = JobReview(
            job=JobExtraction(),
            assessment=assessment,
            career_score=50,
            status=ReviewStatus.APPROVED,
            overrides=[
                HumanOverride(
                    criterion="transformation",
                    original_score=1,
                    human_score=2,
                    reason="Regression test override",
                )
            ],
            ai_runs=[
                AIRunMetadata(
                    run_type="assessment",
                    model_name="test-model",
                    prompt_version="test-prompt",
                    rubric_version="test-rubric",
                    status="success",
                    latency_seconds=1.25,
                )
            ],
        )

        job_id = database.save_approved_job(review, "Job description")

        with sqlite3.connect(database.DATABASE_NAME) as connection:
            rows = connection.execute(
                "SELECT evidence FROM assessments WHERE job_id = ?",
                (job_id,),
            ).fetchall()

        self.assertEqual(len(rows), 7)
        self.assertEqual(
            json.loads(rows[0][0]),
            ["First piece of evidence", "Second piece"],
        )
        effective_scores = get_effective_assessment_scores(job_id)
        self.assertEqual(effective_scores["transformation"], 2)
        self.assertEqual(effective_scores["business_ownership"], 1)
        ai_runs = get_job_ai_runs(job_id)
        self.assertEqual(len(ai_runs), 1)
        self.assertEqual(ai_runs[0]["rubric_version"], "test-rubric")
        self.assertEqual(ai_runs[0]["latency_seconds"], 1.25)

    def test_evaluation_summary_returns_integer_counts(self) -> None:
        summary = get_evaluation_summary()

        self.assertEqual(
            summary,
            {
                "total_jobs": 0,
                "total_assessments": 0,
                "total_override_events": 0,
            },
        )
        self.assertTrue(
            all(type(value) is int for value in summary.values())
        )


if __name__ == "__main__":
    unittest.main()