from typing import List, Optional

from pydantic import BaseModel, Field


class JobProfile(BaseModel):
    job_id: str

    title: str

    company: Optional[str] = None

    description: Optional[str] = None

    required_skills: List[str] = Field(default_factory=list)

    preferred_skills: List[str] = Field(default_factory=list)

    minimum_experience: float = Field(default=0.0, ge=0)

    education: Optional[str] = None

    keywords: List[str] = Field(default_factory=list)