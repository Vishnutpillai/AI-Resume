from typing import Dict, List

from app.schemas.resume import ResumeProfile
from app.schemas.job import JobProfile


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name for reliable comparison.
    """
    if not skill:
        return ""

    skill = skill.lower().strip()

    # Common aliases
    aliases = {
        "scikit learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "amazon web services": "aws",
        "natural language processing": "nlp",
        "exploratory data analysis": "eda",
    }

    return aliases.get(skill, skill)


def normalize_skill_list(skills: List[str]) -> set[str]:
    """
    Normalize a list of skills and remove empty values.
    """
    return {
        normalize_skill(skill)
        for skill in skills
        if normalize_skill(skill)
    }


def calculate_skill_score(
    resume_skills: List[str],
    job_skills: List[str],
) -> float:
    """
    Calculate percentage of job skills covered by the resume.

    Returns:
        Score between 0 and 100.
    """
    job_set = normalize_skill_list(job_skills)

    if not job_set:
        return 0.0

    resume_set = normalize_skill_list(resume_skills)

    matched = resume_set.intersection(job_set)

    return round((len(matched) / len(job_set)) * 100, 2)


def match_skills(
    resume_skills: List[str],
    job_skills: List[str],
) -> Dict[str, object]:
    """
    Compare resume skills against job skills.

    Returns:
        matched skills
        missing skills
        score
    """
    job_set = normalize_skill_list(job_skills)
    resume_set = normalize_skill_list(resume_skills)

    matched = sorted(resume_set.intersection(job_set))
    missing = sorted(job_set - resume_set)

    score = calculate_skill_score(
        resume_skills=resume_skills,
        job_skills=job_skills,
    )

    return {
        "matched": matched,
        "missing": missing,
        "score": score,
    }


def match_required_and_preferred_skills(
    resume: ResumeProfile,
    job: JobProfile,
) -> Dict[str, object]:
    """
    Match resume skills against required and preferred job skills.
    """

    required_result = match_skills(
        resume_skills=resume.skills,
        job_skills=job.required_skills,
    )

    preferred_result = match_skills(
        resume_skills=resume.skills,
        job_skills=job.preferred_skills,
    )

    return {
        "required": required_result,
        "preferred": preferred_result,
    }