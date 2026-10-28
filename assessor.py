import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from models import JobExtraction, JobAssessment
from criteria import CAREER_CRITERIA

load_dotenv()  # Load environment variables from .env file

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ASSESSMENT_PROMPT_VERSION = "1.0"
MODEL_NAME = "gpt-5.6"

def assess_job(job_description: str, job_extraction: JobExtraction) -> JobAssessment:
    criteria_text = json.dumps(
        CAREER_CRITERIA,
        indent=2
    )

    extracted_job_text = job_extraction.model_dump_json(
        indent=2
    )

    prompt = f"""
    You are evaluating a job against predefined career criteria.

    Your task is NOT to decide whether the candidate should accept
    the job.

    Your task is to evaluate the evidence in the job description
    against each career criterion.

    SCORING RULES:

    0 = No meaningful evidence
    1 = Some evidence
    2 = Strong evidence

    For every criterion:

    1. Give a score from 0 to 2.
    2. Explain the evidence supporting the score.
    3. Give confidence from 0 to 1.

    IMPORTANT RULES:

    - Only use evidence supported by the job description.
    - Do not invent responsibilities.
    - Do not assume missing information.
    - Distinguish current responsibilities from future opportunities.
    - If information is unclear or missing, lower the confidence.
    - Add important unknown information to missing_information.

    CAREER CRITERIA:

    {criteria_text}

    STRUCTURED JOB INFORMATION:

    {extracted_job_text}

    ORIGINAL JOB DESCRIPTION:

    {job_description}
    """

    response = client.responses.parse(
        model = MODEL_NAME,
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        text_format=JobAssessment
    )

    return response.output_parsed