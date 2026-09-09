import json

from app.schemas.job import JobProfile
from src.extraction.skill_extractor import extract_skills


def extract_job(
    text: str,
    job_id: str,
    title: str,
) -> JobProfile:
    """
    Extract a JobProfile from JSON or plain-text job description.

    For JSON input, preserve the structured JD fields.
    For plain text input, extract skills automatically.
    """

    # ---------------------------------------------------------
    # Try structured JSON extraction first
    # ---------------------------------------------------------
    try:
        data = json.loads(text)

        if isinstance(data, dict):
            required_skills = data.get("required_skills") or []
            preferred_skills = data.get("preferred_skills") or []
            keywords = data.get("keywords") or []

            # If structured skills are missing, infer them
            # from the description.
            description = data.get("description") or ""

            if not required_skills:
                required_skills = extract_skills(description)

            if not keywords:
                keywords = extract_skills(description)

            return JobProfile(
                job_id=data.get("job_id") or job_id,
                title=data.get("title") or title,
                company=data.get("company"),
                description=description,
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                minimum_experience=float(
                    data.get("minimum_experience") or 0
                ),
                education=data.get("education"),
                keywords=keywords,
            )

    except (json.JSONDecodeError, TypeError, ValueError):
        pass

    # ---------------------------------------------------------
    # Plain-text fallback
    # ---------------------------------------------------------
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