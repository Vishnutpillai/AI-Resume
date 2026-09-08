from app.schemas.job import JobProfile
from src.extraction.skill_extractor import extract_skills


def extract_job(
    text: str,
    job_id: str,
    title: str,
) -> JobProfile:
    """
    Convert job description text into a structured JobProfile.
    """

    skills = extract_skills(text)

    return JobProfile(
        job_id=job_id,
        title=title,
        description=text,
        required_skills=skills,
        preferred_skills=[],
        minimum_experience=0.0,
        education=None,
        keywords=skills,
    )