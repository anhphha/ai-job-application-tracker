import os

from dotenv import load_dotenv
from openai import OpenAI

from models import JobExtraction

load_dotenv()  # Load environment variables from .env file

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


EXTRACTION_PROMPT_VERSION = "1.0"
MODEL_NAME = "gpt-5.6"


def extract_job(job_description: str) -> JobExtraction:
    EXTRACTION_PROMPT = f"""
    You are extracting structured information from a job description.

    If information is missing, return null.

    Rules:
    - Only use information explicitly supported by the job description.
    - Do not invent missing information.
    - If something is not specified, return null or an empty list.
    - Distinguish required skills from preferred skills.

    Extract:

    - company
    - job title
    - location
    - application deadline
    - responsibilities
    - required skills
    - preferred skills
    - seniority

    Return structured output matching the supplied schema.

    Job description:

    {job_description}
    """

    response = client.responses.parse(
        model = MODEL_NAME,
        input=[
            {
                "role": "user",
                "content": EXTRACTION_PROMPT
            }
        ],
        text_format=JobExtraction
    )

    return response.output_parsed

