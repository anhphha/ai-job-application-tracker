import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from extractor import extract_job, JobExtraction

job_description_1 = """
Acme Corporation is looking for a Data Transformation Analyst
in Helsinki.

You will work with business and technology teams to improve
data processes and support digital transformation initiatives.

Responsibilities include:
- analyzing business processes
- building Power BI reports
- working with senior stakeholders
- supporting transformation projects

Required skills:
- SQL
- Power BI
- English

Python is considered an advantage.
"""


job_description_2 = """
We are hiring a Data Analyst.

You will analyze business data and work with stakeholders.
"""


job_description_3 = """
We are hiring a Data Analyst.

Python is an advantage
"""


result_1 = extract_job(job_description_1)
print(result_1.model_dump_json(indent=2))

result_2 = extract_job(job_description_2)
print(result_2.model_dump_json(indent=2))

result_3 = extract_job(job_description_3)
print(result_3.model_dump_json(indent=2))