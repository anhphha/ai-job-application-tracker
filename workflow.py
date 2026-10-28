from enum import Enum
from dataclasses import dataclass, field
from models import JobAssessment, JobExtraction, AIRunMetadata
from typing import Optional

EDITABLE_CRITERIA = [
    "transformation",
    "business_ownership",
    "stakeholder_exposure",
    "data_relevance",
    "decision_influence",
    "change_adoption",
    "leadership_potential"
]

class ReviewStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"

@dataclass
class JobReview:
    job: JobExtraction
    assessment: JobAssessment
    career_score: float

    status: ReviewStatus = (ReviewStatus.PENDING)

    overrides: list["HumanOverride"] = field(default_factory=list)

    ai_runs: list[AIRunMetadata] = field(default_factory=list)

@dataclass
class HumanOverride:
    criterion: str
    original_score: int
    human_score: int
    reason: str
    is_active: bool = True

def approve_review(review: JobReview) -> None:
    review.status = ReviewStatus.APPROVED


def reject_review(review: JobReview) -> None:
    review.status = ReviewStatus.REJECTED


def add_override(review: JobReview, criterion: str, human_score: int, reason: str) -> None:

    if criterion not in EDITABLE_CRITERIA:
        raise ValueError(
            f"Invalid criterion: {criterion}"
        )

    if human_score not in [0, 1, 2]:
        raise ValueError("Human score must be 0, 1, or 2.")

    if not reason.strip():
        raise ValueError(
            "Override reason cannot be empty."
        )

    criterion_result = getattr(review.assessment, criterion)

    # Deactivate previous active override
    for existing_override in review.overrides:
        if existing_override.criterion == criterion and existing_override.is_active:
            existing_override.is_active = False


    # Create new override
    override = HumanOverride(
        criterion=criterion,
        original_score = criterion_result.score,
        human_score=human_score,
        reason=reason.strip(),
        is_active=True
    )

    review.overrides.append(override)

def revert_override(review: JobReview, criterion: str) -> None:
    if criterion not in EDITABLE_CRITERIA:
        raise ValueError(
            f"Invalid criterion: {criterion}"
        )
    for override in reversed(review.overrides):
        if override.criterion == criterion and override.is_active:
            override.is_active = False
            return
    raise ValueError(
        f"No active override found for criterion: {criterion}"
    )

def get_effective_score(review: JobReview, criterion: str) -> int:

    for override in reversed(review.overrides):
        if override.criterion == criterion and override.is_active:
            return override.human_score

    criterion_result = getattr(review.assessment, criterion)
    return criterion_result.score

def get_human_overrides(review: JobReview, criterion: Optional[str] = None) -> list[HumanOverride]:
    for override in reversed(review.overrides):
        if criterion is None or override.criterion == criterion and override.is_active:
            return override
    return None

def can_persist(review: JobReview) -> bool:
    return review.status == ReviewStatus.APPROVED

