import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from extractor import extract_job
from assessor import assess_job
from scoring import calculate_weighted_score, find_low_confidence_items, calculate_reviewed_score
from workflow import JobReview, ReviewStatus, approve_review, reject_review, can_persist, add_override, revert_override, get_human_overrides, get_effective_score
from database import initialize_database, save_approved_job


def main() -> None:
    job_description = """
    Acme Corporation is hiring a Data Transformation Analyst
    in Helsinki.

    You will work directly with business leaders and technology
    teams to improve how the company uses data.

    Responsibilities include:

    - analyzing existing business processes
    - identifying opportunities for process improvement
    - developing Power BI analytics
    - recommending improvements to senior stakeholders
    - supporting implementation of new processes
    - training business users on new analytics solutions

    Required skills:

    - SQL
    - Power BI
    - stakeholder communication

    Python is considered an advantage.

    The successful candidate may later take responsibility for
    leading transformation workstreams.
    """


    initialize_database()

    # STEP 1 — AI Extraction

    extracted_job = extract_job(
        job_description
    )

    # STEP 2 — AI Assessment

    assessment = assess_job(
        job_description,
        extracted_job
    )

    # STEP 3 — Deterministic scoring

    career_fit_score = calculate_weighted_score(
        assessment
    )

    review = JobReview(
        job=extracted_job,
        assessment=assessment,
        career_score=career_fit_score
    )


    review_items = find_low_confidence_items(
        assessment
    )

    # ADD OVERRIDE EXAMPLE
    add_override(
        review,
        criterion="business_ownership",
        human_score=1,
        reason=(
            "The role contributes to business outcomes, "
            "but explicit ownership is not defined."
        )
    )

    revert_override(
        review,
        criterion="business_ownership"
    )


    # CALCULATE REVIEWED SCORE

    reviewed_score = calculate_reviewed_score(
        review
    )

    print(
        "Original AI score:",
        review.career_score
    )

    print(
        "Human-reviewed score:",
        reviewed_score
    )


    # OUTPUT

    print("\n-----------------------------")
    print("JOB")
    print("-----------------------------")

    print("Company:", extracted_job.company)
    print("Role:", extracted_job.role)
    print("Location:", extracted_job.location)


    print("\n-----------------------------")
    print("CAREER ASSESSMENT")
    print("-----------------------------")

    for criterion_name in [
        "transformation",
        "business_ownership",
        "stakeholder_exposure",
        "data_relevance",
        "decision_influence",
        "change_adoption",
        "leadership_potential"
    ]:

        ai_result = getattr(
            assessment,
            criterion_name
        )

        human_override = get_human_overrides(
            review,
            criterion_name
        )

        effective_score = get_effective_score(
            review,
            criterion_name
        )

        print(f"\n{criterion_name}")

        print(
            "AI:",
            ai_result.score,
            "/ 2"
        )

        if human_override:
            print("Human:", human_override.human_score, "/ 2")
        else:
            print("Human: —")

        print("Effective:", effective_score, "/ 2")


    print("\n-----------------------------")
    print("STRATEGIC CAREER FIT SCORE")
    print("-----------------------------")

    print(
        career_fit_score,
        "/ 100"
    )


    print("\n-----------------------------")
    print("HUMAN REVIEW")
    print("-----------------------------")

    if review_items:
        print("\n⚠ ATTENTION")
        print(
            "The following criteria have "
            "low-confidence AI assessments:"
        )
        for item in review_items:
            print("-", item)
    else:

        print(
            "✓ No low-confidence criteria detected."
        )


    print("\n-----------------------------")
    print("MISSING INFORMATION")
    print("-----------------------------")

    if assessment.missing_information:
        for item in assessment.missing_information:
            print("-", item)
    else:
        print("No important missing information.")



    print("\n-----------------------------")
    print("HUMAN DECISION")
    print("-----------------------------")


    decision = input(
        "Approve, edit, or reject? [a/e/r]: "
    ).strip().lower()


    if decision == "a":
        approve_review(review)
    elif decision == "r":
        reject_review(review)
    elif decision == "e":
        criterion_to_edit = input(
            "Which criterion do you want to edit?"
        ).strip()

        if criterion_to_edit not in [
            "transformation",
            "business_ownership",
            "stakeholder_exposure",
            "data_relevance",
            "decision_influence",
            "change_adoption",
            "leadership_potential"
        ]:
            print("Invalid criterion.")
        else:
            new_score = int(input(
                f"Enter new score for {criterion_to_edit} (0, 1, or 2): "
            ).strip())

            reason = input(
                f"Enter reason for changing {criterion_to_edit}: "
            ).strip()

            add_override(
                review,
                criterion=criterion_to_edit,
                human_score=new_score,
                reason=reason
            )

            reviewed_score = calculate_reviewed_score(
                review
            )
    else:
        print(
            "Invalid decision. "
            "\nReview remains pending."
        )

    print(
        "\nFinal review status:",
        review.status.value
    )

    if can_persist(review):
        print(
            "✓ Approved. "
            "This job may be saved to the database."
        )

        job_id = save_approved_job(
            review,
            job_description
        )


        print("\n✓ Job saved successfully.")

        print("Database job ID:",job_id)
    else:
        print(
            "✗ Not approved. "
            "\nDatabase write is blocked."
        )


    print("\n-----------------------------")
    print("HUMAN OVERRIDES")
    print("-----------------------------")

    if review.overrides:
        for override in review.overrides:
            print("Criterion:", override.criterion)

            print("AI score:", override.original_score)

            print("Human score:", override.human_score)

            print("Reason:", override.reason)

            print(
                "Recalculated score:", calculate_reviewed_score(review)
            )
            print()
            print(review.overrides)
            print()
    else:
        print("No human overrides.")




if __name__ == "__main__":
    main()
