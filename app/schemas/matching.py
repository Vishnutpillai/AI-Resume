from typing import List

from pydantic import BaseModel, Field


class SkillMatch(BaseModel):
    matched: List[str] = Field(default_factory=list)
    missing: List[str] = Field(default_factory=list)


class MatchBreakdown(BaseModel):
    required_skill_score: float = 0.0
    semantic_score: float = 0.0
    experience_score: float = 0.0
    project_score: float = 0.0
    education_score: float = 0.0
    preferred_skill_score: float = 0.0


class MatchResult(BaseModel):
    candidate_id: str
    job_id: str

    overall_score: float = Field(default=0.0, ge=0, le=100)

    breakdown: MatchBreakdown

    skill_match: SkillMatch = Field(default_factory=SkillMatch)

    strengths: List[str] = Field(default_factory=list)

    weaknesses: List[str] = Field(default_factory=list)

    recommendations: List[str] = Field(default_factory=list)