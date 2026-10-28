from models import JobAssessment
from criteria import CAREER_CRITERIA
from workflow import JobReview, get_effective_score

def calculate_weighted_score(job_assessment: JobAssessment) -> float:
    total_score = 0

    for criterion_name, criterion in CAREER_CRITERIA.items():

        criterion_result = getattr(
            job_assessment,
            criterion_name
        )

        ai_score = criterion_result.score
        weight = criterion["weight"]

        normalized_score = ai_score / 2  # Normalize score to [0, 1]

        weighted_score = normalized_score * weight
        total_score += weighted_score

    final_score = total_score * 100  # Convert to percentage

    return round(final_score, 1)


def find_low_confidence_items(job_assessment: JobAssessment, threshold: float = 0.7) -> list[str]:  # Define a threshold for low confidence

    reviewed_items = []

    for criterion_name in CAREER_CRITERIA.keys():
        criterion_result = getattr(
            job_assessment,
            criterion_name
        )

        if criterion_result.confidence < threshold:
            reviewed_items.append(criterion_name)

    return reviewed_items


def calculate_reviewed_score(review: JobReview) -> float:
    total_score = 0

    for criterion_name, criterion in CAREER_CRITERIA.items():

        effective_score = get_effective_score(review, criterion_name)
        weight = criterion["weight"]

        normalized_score = effective_score / 2  # Normalize score to [0, 1]

        weighted_score = normalized_score * weight
        total_score += weighted_score

    final_score = total_score * 100  # Convert to percentage

    return round(final_score, 1)