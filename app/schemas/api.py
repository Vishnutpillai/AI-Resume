from typing import Optional

from pydantic import BaseModel, Field


class ResumeAnalysisRequest(BaseModel):
    candidate_id: str
    name: Optional[str] = None
    summary: Optional[str] = None
    skills: list[str] = Field(default_factory=list)
    resume_text: str


class JobAnalysisRequest(BaseModel):
    job_id: str
    title: str
    company: Optional[str] = None
    description: Optional[str] = None
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    minimum_experience: float = Field(default=0.0, ge=0)
    education: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
    job_text: str


class AnalysisRequest(BaseModel):
    resume: dict
    job: dict
    resume_text: str
    job_text: str
    use_llm: bool = True

class JobRecommendationRequest(BaseModel):
    resume: dict
    resume_text: str
    jobs: list[dict] = Field(default_factory=list)
    job_texts: list[str] = Field(default_factory=list)