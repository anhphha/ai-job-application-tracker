from pydantic import BaseModel, Field
from typing import Optional

class JobExtraction(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    location: Optional[str] = None
    deadline: Optional[str] = None

    responsibilities: list[str] = []
    required_skills: list[str] = []
    preferred_skills: list[str] = []

    seniority: Optional[int] = None

class CriterionAssessment(BaseModel):
    score: int = Field(ge=0, le=2)
    evidence: list[str]
    reasoning: str
    confidence: float = Field(ge=0, le=1)

class JobAssessment(BaseModel):
    transformation: CriterionAssessment
    business_ownership: CriterionAssessment
    stakeholder_exposure: CriterionAssessment
    data_relevance: CriterionAssessment
    decision_influence: CriterionAssessment
    change_adoption: CriterionAssessment
    leadership_potential: CriterionAssessment

    missing_information: list[str] = []

class AIRunMetadata(BaseModel):
    run_type: str

    model_name: str
    prompt_version: str

    rubric_version: Optional[str] = None

    status: str

    latency_seconds : Optional[float] = None

    error_message: Optional[str]=None


