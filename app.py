import streamlit as st
import pandas as pd
import time

from database import initialize_database, save_approved_job, get_all_jobs, get_job_by_id, get_job_assessments, get_job_overrides, get_job_missing_information, get_effective_assessment_scores, get_job_ai_runs, get_override_statistics, get_override_direction_statistics, get_evaluation_summary, get_active_override_count
from extractor import extract_job, EXTRACTION_PROMPT_VERSION, MODEL_NAME as EXTRACTION_MODEL
from assessor import assess_job, ASSESSMENT_PROMPT_VERSION, MODEL_NAME as ASSESSMENT_MODEL
from scoring import calculate_weighted_score, calculate_reviewed_score, find_low_confidence_items
from workflow import JobReview, ReviewStatus, add_override, revert_override, approve_review, reject_review, get_effective_score, get_human_overrides
from criteria import CAREER_CRITERIA, RUBRIC_VERSION
from models import AIRunMetadata

APP_VERSION = "0.1.0"

initialize_database()

if "review" not in st.session_state:
    st.session_state.review = None

if "job_description" not in st.session_state:
    st.session_state.job_description = None

if "saved_job_id" not in st.session_state:
    st.session_state.saved_job_id = None


st.set_page_config(
    page_title="AI Job Tracker",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Analyze Job",
        "Saved Jobs",
        "Evaluation"
    ]
)

st.sidebar.caption(
    f"Version {APP_VERSION}"
)

if page == "Analyze Job":
    st.title("🤖 AI Job Tracker | Made by Anh Ha")

    st.write(
    "Welcome to the AI Job Tracker. "
    "Evaluate job opportunities against strategic career criteria "
    "using AI-assisted analysis and human review."
    )

    job_description = st.text_area(
        "Enter the job description below:",
        height=400,
        placeholder="Paste the job description here...",
    )

    analyze_button = st.button(
        "Analyze Job Description",
        type="primary",
        use_container_width=True,
        disabled=not job_description.strip(),
    )

    if analyze_button:

        extraction_start = time.perf_counter()

        with st.spinner("Extracting job information..."):


            job_extraction = extract_job(job_description)

        extraction_latency = (time.perf_counter() - extraction_start)


        assessment_start = time.perf_counter()

        with st.spinner("Assessing job against career criteria..."):


            job_assessment = assess_job(
                job_description,
                job_extraction
            )

        assessment_latency = (time.perf_counter() - assessment_start)


        career_score = calculate_weighted_score(job_assessment)

        job_review = JobReview(
            job=job_extraction,
            assessment=job_assessment,
            career_score=career_score,
            ai_runs=[
                AIRunMetadata(
                    run_type="extraction",
                    model_name=EXTRACTION_MODEL,
                    prompt_version=EXTRACTION_PROMPT_VERSION,
                    rubric_version=None,
                    status="success",
                    latency_seconds=extraction_latency,
                ),
                AIRunMetadata(
                    run_type="assessment",
                    model_name=ASSESSMENT_MODEL,
                    prompt_version=ASSESSMENT_PROMPT_VERSION,
                    rubric_version=RUBRIC_VERSION,
                    status="success",
                    latency_seconds=assessment_latency,
                ),
            ],
        )

        st.session_state.review = job_review
        st.session_state.job_description = job_description


    if st.session_state.review is not None:

        review = st.session_state.review

        st.divider()

        st.subheader("Job")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Company**")
            st.write(
                review.job.company or "Unknown"
            )

        with col2:
            st.write("**Role**")
            st.write(
                review.job.role or "Unknown"
            )

        with col3:
            st.write("**Location**")
            st.write(
                review.job.location or "Unknown"
            )

        reviewed_score = calculate_reviewed_score(
            review
        )

        st.subheader(
            "Strategic Career Fit"
        )

        st.metric(
            label="Career Direction Score",
            value=f"{reviewed_score}/100"
        )

        st.subheader(
            "Career Assessment"
        )

        for criterion_name in CAREER_CRITERIA:
            result = getattr(
                review.assessment,
                criterion_name
            )

            effective_score = get_effective_score(
                review,
                criterion_name
            )

            human_override = get_human_overrides(
                review,
                criterion_name
            )

            with st.expander(
                criterion_name.replace(
                    "_",
                    " "
                ).title()
            ):

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.metric(
                        "AI Score",
                        f"{result.score}/2"
                    )

                with col2:

                    if human_override:

                        st.metric(
                            "Human Score",
                            f"{human_override.human_score}/2"
                        )

                    else:

                        st.metric(
                            "Human Score",
                            "—"
                        )

                with col3:

                    st.metric(
                        "Effective Score",
                        f"{effective_score}/2"
                    )

                st.write(
                    "**Evidence**"
                )

                st.write(
                    result.evidence
                    or "No evidence provided."
                )

                st.write(
                    f"**Confidence:** "
                    f"{result.confidence:.0%}"
                )

                st.divider()

                st.write(
                    "**Human Review**"
                )

                human_score = st.selectbox(
                    "Override score",
                    options=[
                        "No override",
                        0,
                        1,
                        2
                    ],
                    key=f"score_{criterion_name}"
                )

                override_reason = st.text_input(
                    "Reason",
                    key=f"reason_{criterion_name}"
                )

                if st.button(
                    "Apply Override",
                    key=f"apply_{criterion_name}"
                ):

                    if human_score == "No override":

                        st.warning(
                            "Select a human score first."
                        )

                    elif not override_reason.strip():

                        st.warning(
                            "Please provide a reason."
                        )

                    else:

                        add_override(
                            review,
                            criterion_name,
                            human_score,
                            override_reason
                        )

                        st.success(
                            "Override applied."
                        )

                        st.rerun()

                if human_override:

                    st.info(
                        f"Active human override: "
                        f"{human_override.human_score}/2\n\n"
                        f"Reason: "
                        f"{human_override.reason}"
                    )

                    if st.button(
                        "Revert Override",
                        key=f"revert_{criterion_name}"
                    ):

                        revert_override(
                            review,
                            criterion_name
                        )

                        st.rerun()


        if review.assessment.missing_information:

            st.subheader(
                "Missing Information"
            )

            for item in (
                review.assessment.missing_information
            ):

                st.write(
                    f"• {item}"
                )


        low_confidence_items = (
            find_low_confidence_items(
                review.assessment
            )
        )

        if low_confidence_items:

            st.warning(
                "Human review recommended for "
                "low-confidence criteria."
            )

            for item in low_confidence_items:

                st.write(
                    f"• {item.replace('_', ' ').title()}"
                )


        st.divider()

        st.subheader(
            "Final Decision"
        )

        approve_col, reject_col = st.columns(2)

        with approve_col:

            if st.button(
                "Approve",
                type="primary",
                use_container_width=True
            ):

                approve_review(review)

                st.rerun()

        with reject_col:

            if st.button(
                "Reject",
                use_container_width=True
            ):

                reject_review(
                    review
                )

                st.rerun()

        st.write(
            "**Review Status:**",
            review.status.value.upper()
        )

        if review.status == ReviewStatus.APPROVED:
            if st.session_state.saved_job_id is not None:
                st.success(
                f"Saved as Job ID "
                f"{st.session_state.saved_job_id}"
            )
            else:
                if st.button(
                    "Save Approved Job",
                    use_container_width=True
                ):

                    job_id = save_approved_job(
                        review,
                        st.session_state.job_description
                    )

                    st.session_state.saved_job_id = job_id

                    st.success(
                        f"Job saved successfully. "
                        f"Database ID: {job_id}"
                    )


elif page == "Saved Jobs":

    st.title(
        "Saved Jobs"
    )

    st.write(
        "Review and compare approved "
        "job opportunities."
    )

    jobs = get_all_jobs()

    job_options = {
        f"{job['company']} — {job['role']} (#{job['id']})":
            job["id"]
        for job in jobs
    }

    selected_job_label = st.selectbox(
        "View job details",
        options=list(
            job_options.keys()
        )
    )

    selected_job_id = (
        job_options[
            selected_job_label
        ]
    )

    selected_job = get_job_by_id(
        selected_job_id
    )

    selected_assessments = (
        get_job_assessments(
            selected_job_id
        )
    )

    selected_overrides = (
        get_job_overrides(
            selected_job_id
        )
    )


    if not jobs:

        st.info(
            "No approved jobs saved yet."
        )

    else:

        st.write(
            f"Saved jobs: {len(jobs)}"
        )

        for job in jobs:

            with st.container(
                border=True
            ):

                col1, col2, col3 = (
                    st.columns(
                        [3, 2, 1]
                    )
                )

                with col1:

                    st.subheader(
                        job["role"]
                        or "Unknown Role"
                    )

                    st.write(
                        job["company"]
                        or "Unknown Company"
                    )

                    st.caption(
                        job["location"]
                        or "Unknown Location"
                    )

                with col2:

                    st.metric(
                        "Strategic Fit",
                        f"{job['reviewed_career_score']}/100"
                    )

                with col3:

                    st.write(
                        f"ID: {job['id']}"
                    )

                    st.write(
                        job["status"].upper()
                    )



    st.divider()

    st.subheader(
        selected_job["role"]
    )

    st.write(
        f"**Company:** "
        f"{selected_job['company']}"
    )

    st.write(
        f"**Location:** "
        f"{selected_job['location']}"
    )

    score_col1, score_col2 = (
        st.columns(2)
    )

    with score_col1:

        st.metric(
            "Original AI Score",
            selected_job[
                "ai_career_score"
            ]
        )

    with score_col2:

        st.metric(
            "Human-reviewed Score",
            selected_job[
                "reviewed_career_score"
            ]
        )


    st.subheader(
        "Assessment"
    )

    for assessment in selected_assessments:

        criterion_name = assessment[
            "criterion"
        ]

        with st.expander(
            criterion_name
            .replace("_", " ")
            .title()
        ):

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "AI Score",
                    f"{assessment['ai_score']}/2"
                )

            with col2:

                st.metric(
                    "Confidence",
                    f"{assessment['confidence']:.0%}"
                )

            st.write(
                "**Evidence**"
            )

            st.write(
                assessment["evidence"]
                or "No evidence recorded."
            )


    with st.expander(
        "AI Run Information"
    ):
        ai_runs = (
            get_job_ai_runs(
                selected_job_id
            )
        )

        if not ai_runs:

            st.info(
                "AI run metadata was not recorded"
                "for this earlier assessment."
            )

        else:

            for run in ai_runs:

                st.write(
                    f"**{run['run_type'].title()}**"
                )

                st.write(
                    f"Model: {run['model_name']}"
                )

                st.write(
                    f"Prompt version: "
                    f"{run['prompt_version']}"
                )

                if run["rubric_version"]:

                    st.write(
                        f"Rubric version: "
                        f"{run['rubric_version']}"
                    )

                if run["latency_seconds"] is not None:

                    st.write(
                        f"Latency: "
                        f"{run['latency_seconds']:.2f}s"
                    )

                st.write(
                    f"Status: {run['status']}"
                )

                st.divider()


    st.subheader(
        "Missing Information"
    )


    missing_information = (
        get_job_missing_information(
            selected_job_id
        )
    )


    if missing_information:

        for item in missing_information:

            st.write(
                f"• {item}"
            )

    else:

        st.write(
            "No missing information recorded."
        )

    st.subheader(
    "Human Review History"
    )

    if not selected_overrides:

        st.write(
            "No human overrides recorded."
        )
    else:

        for override in selected_overrides:

            status = (
                "Active"
                if override["is_active"]
                else "Reverted"
            )

            with st.container(
                border=True
            ):

                st.write(
                    f"**Criterion:** "
                    f"{override['criterion']}"
                )

                st.write(
                    f"AI: "
                    f"{override['original_score']}/2"
                )

                st.write(
                    f"Human: "
                    f"{override['human_score']}/2"
                )

                st.write(
                    f"**Status:** {status}"
                )

                st.write(
                    f"**Reason:** "
                    f"{override['reason']}"
                )

    st.divider()

    st.header("Compare Jobs")

    comparison_labels = st.multiselect(
        "Select jobs to compare",
        options=list(
            job_options.keys()
        ),
        max_selections=3
    )

    if len(comparison_labels) >= 2:
        comparison_jobs = []

        for label in comparison_labels:
            job_id = job_options[label]

            job = get_job_by_id(job_id)

            comparison_jobs.append(job)


        columns = st.columns(
            len(comparison_jobs)
        )

        for column, job in zip(
            columns,
            comparison_jobs
        ):

            with column:
                st.subheader(job["company"])

                st.write("Role: ", job["role"])

                st.metric(
                    "Strategic Fit",
                    f"{job['reviewed_career_score']}/100")

        effective_scores = {}

        for label in comparison_labels:
            job_id = job_options[label]
            effective_scores[label] = get_effective_assessment_scores(job_id)

        comparison_rows = []

        for criterion_name in CAREER_CRITERIA:
            row = {
                "Criterion":
                    criterion_name
                    .replace("_", " ")
                    .title(),

                "Weight" :
                    f"{CAREER_CRITERIA[criterion_name]['weight']:.0%}"
            }

            for label in comparison_labels:

                row[label] = effective_scores[label][criterion_name]

            comparison_rows.append(row)

        comparison_df = pd.DataFrame(comparison_rows)

        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True
        )


elif page == "Evaluation":

    st.title(
        " AI Evaluation"
    )

    st.write(
        "Monitor human overrides and"
        "AI assessment behavior."
    )

    override_stats = (
        get_override_statistics()
    )

    if not override_stats:

        st.info(
            "No human overrides recorded yet."
        )

    else:

        st.subheader(
            "Human Override Events"
        )

        for item in override_stats:

            criterion = (
                item["criterion"]
                .replace("_", " ")
                .title()
            )

            st.write(
                f"**{criterion}:** "
                f"{item['override_count']}"
            )

        summary = get_evaluation_summary()

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Jobs Evaluated",
                summary["total_jobs"]
            )

        with col2:

            st.metric(
                "Criterion Assessments",
                summary[
                    "total_assessments"
                ]
            )

        with col3:

            st.metric(
                "Human Override Events",
                summary[
                    "total_override_events"
                ]
            )

        active_overrides = (
            get_active_override_count()
        )

        total_assessments = (
            summary["total_assessments"]
        )

        if total_assessments:

            disagreement_rate = (
                active_overrides/ total_assessments * 100
            )

        else:

            disagreement_rate = 0

        st.metric(
            "Current AI-Human Disagreement",
            f"{disagreement_rate:.1f}%"
        )

