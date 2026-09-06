from typing import List, Optional

from pydantic import BaseModel, Field


class Education(BaseModel):
    degree: str
    field: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[int] = None


class Experience(BaseModel):
    company: Optional[str] = None
    role: str
    years: float = Field(default=0.0, ge=0)


class Project(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    candidate_id: str
    name: Optional[str] = None
    summary: Optional[str] = None

    skills: List[str] = Field(default_factory=list)

    education: List[Education] = Field(default_factory=list)

    experience: List[Experience] = Field(default_factory=list)

    projects: List[Project] = Field(default_factory=list)

    certifications: List[str] = Field(default_factory=list)