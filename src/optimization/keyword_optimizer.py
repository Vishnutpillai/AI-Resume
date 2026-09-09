from app.schemas.resume import ResumeProfile
from app.schemas.job import JobProfile
from src.matching.skill_matcher import normalize_skill


def find_resume_keywords(
    resume: ResumeProfile,
    job: JobProfile,
) -> dict[str, list[str]]:
    """
    Identify job-relevant keywords already supported by the resume.

    The optimizer only recommends keywords that are already present
    in the candidate's resume profile.
    """

    resume_skills = {
        normalize_skill(skill)
        for skill in resume.skills
        if normalize_skill(skill)
    }

    required = {
        normalize_skill(skill)
        for skill in job.required_skills
        if normalize_skill(skill)
    }

    preferred = {
        normalize_skill(skill)
        for skill in job.preferred_skills
        if normalize_skill(skill)
    }

    matched_required = sorted(
        resume_skills.intersection(required)
    )

    matched_preferred = sorted(
        resume_skills.intersection(preferred)
    )

    missing_required = sorted(
        required - resume_skills
    )

    missing_preferred = sorted(
        preferred - resume_skills
    )

    return {
        "matched_required_keywords": matched_required,
        "matched_preferred_keywords": matched_preferred,
        "missing_required_keywords": missing_required,
        "missing_preferred_keywords": missing_preferred,
    }