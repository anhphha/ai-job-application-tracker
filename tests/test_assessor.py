import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from extractor import extract_job
from assessor import assess_job


job_description_1 = """
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

job_description_2 = """
We are hiring a Data Analyst.

Responsibilities:

- Create weekly reports
- Maintain Excel spreadsheets
- Refresh dashboards
- Respond to reporting requests

Required skills:

- Excel
- Power BI
"""

extracted_job_1 = extract_job(job_description_1)
assessment_1 = assess_job(job_description_1, extracted_job_1)
#print(assessment_1.model_dump_json(indent=2))

extracted_job_2 = extract_job(job_description_2)
assessment_2 = assess_job(job_description_2, extracted_job_2)
#print(assessment_2.model_dump_json(indent=2))

print("\n--- CAREER ASSESSMENT ---\n")

criteria = [
    "transformation",
    "business_ownership",
    "stakeholder_exposure",
    "data_relevance",
    "decision_influence",
    "change_adoption",
    "leadership_potential"
]

for criterion in criteria:
    print(criterion.upper())

    for job_number, assessment in enumerate(
        (assessment_1, assessment_2),
        start=1,
    ):
        result = getattr(assessment, criterion)
        print(f"Job {job_number}")
        print("Score:", result.score, "/ 2")
        print("Confidence:", result.confidence)
        print("Evidence:", result.evidence)

    print()