import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from models import CriterionAssessment, JobAssessment, JobExtraction
from workflow import (
    JobReview,
    ReviewStatus,
    approve_review,
    can_persist,
    reject_review,
)


def make_review() -> JobReview:
    criterion = CriterionAssessment(
        score=0,
        evidence=[],
        reasoning="",
        confidence=1.0,
    )
    assessment = JobAssessment(
        transformation=criterion,
        business_ownership=criterion,
        stakeholder_exposure=criterion,
        data_relevance=criterion,
        decision_influence=criterion,
        change_adoption=criterion,
        leadership_potential=criterion,
    )
    return JobReview(
        job=JobExtraction(),
        assessment=assessment,
        career_score=0,
    )


class ReviewWorkflowTests(unittest.TestCase):
    def test_pending_review_cannot_be_persisted(self) -> None:
        review = make_review()

        self.assertFalse(can_persist(review))

    def test_approved_review_can_be_persisted(self) -> None:
        review = make_review()

        approve_review(review)

        self.assertEqual(review.status, ReviewStatus.APPROVED)
        self.assertTrue(can_persist(review))

    def test_rejected_review_cannot_be_persisted(self) -> None:
        review = make_review()

        reject_review(review)

        self.assertEqual(review.status, ReviewStatus.REJECTED)
        self.assertFalse(can_persist(review))


if __name__ == "__main__":
    unittest.main()
