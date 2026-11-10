import sys
from pathlib import Path
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import JobExtraction, JobAssessment
from criteria_v2_1 import CAREER_CRITERIA

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

ASSESSMENT_PROMPT_VERSION = "1.2-candidate"
MODEL_NAME = "gpt-5.6"
PROMPT_FILE = Path(__file__).resolve().parent / "prompts" / "assessment.txt"

def assess_job(job_description: str, job_extraction: JobExtraction) -> JobAssessment:

    template = PROMPT_FILE.read_text(encoding="utf-8")
    required = ("{{CRITERIA}}", "{{EXTRACTION}}", "{{JOB_DESCRIPTION}}")

    if any(template.count(token) != 1 for token in required):
        raise ValueError("Assessment prompt template must contain each placeholder exactly once")

    prompt = (template
        .replace("{{CRITERIA}}", json.dumps(CAREER_CRITERIA, indent=2, ensure_ascii=False))
        .replace("{{EXTRACTION}}", job_extraction.model_dump_json(indent=2))
        .replace("{{JOB_DESCRIPTION}}", job_description))

    response = client.responses.parse(
        model=MODEL_NAME,
        input=[{"role": "user", "content": prompt}],
        text_format=JobAssessment,
    )

    if response.output_parsed is None:
        raise ValueError("Model returned no parsed JobAssessment")

    return response.output_parsed
