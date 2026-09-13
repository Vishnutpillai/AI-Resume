from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.resume import (
    Education,
    Experience,
    Project,
    ResumeProfile,
)

from app.schemas.job import JobProfile


# ============================================================
# RESUME ANALYSIS REQUEST
# ============================================================

class ResumeAnalysisRequest(BaseModel):
    candidate_id: str
    name: str | None = None
    summary: str | None = None

    skills: list[str] = Field(
        default_factory=list
    )

    education: list[Education] = Field(
        default_factory=list
    )

    experience: list[Experience] = Field(
        default_factory=list
    )

    projects: list[Project] = Field(
        default_factory=list
    )

    certifications: list[str] = Field(
        default_factory=list
    )

    resume_text: str


# ============================================================
# JOB ANALYSIS REQUEST
# ============================================================

class JobAnalysisRequest(BaseModel):
    job_id: str
    title: str

    company: str | None = None
    description: str | None = None

    required_skills: list[str] = Field(
        default_factory=list
    )

    preferred_skills: list[str] = Field(
        default_factory=list
    )

    minimum_experience: float = 0.0

    education: str | None = None

    keywords: list[str] = Field(
        default_factory=list
    )

    job_text: str


# ============================================================
# FULL MATCHING / ANALYSIS REQUEST
# ============================================================

class AnalysisRequest(BaseModel):
    resume: ResumeProfile
    job: JobProfile

    resume_text: str
    job_text: str

    use_llm: bool = False


# ============================================================
# JOB RECOMMENDATION REQUEST
# ============================================================

class JobRecommendationRequest(BaseModel):
    resume: ResumeProfile

    resume_text: str

    jobs: list[JobProfile] = Field(
        default_factory=list
    )

    job_texts: list[str] = Field(
        default_factory=list
    )