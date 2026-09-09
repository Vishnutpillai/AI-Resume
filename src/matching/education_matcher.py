import re

from app.schemas.resume import ResumeProfile
from app.schemas.job import JobProfile


DEGREE_ALIASES = {
    "bsc": "bachelor",
    "b.sc": "bachelor",
    "bachelor of science": "bachelor",
    "bachelor's": "bachelor",
    "bachelors": "bachelor",

    "msc": "master",
    "m.sc": "master",
    "master of science": "master",
    "master's": "master",
    "masters": "master",

    "btech": "bachelor",
    "b.tech": "bachelor",
    "be": "bachelor",
    "b.e": "bachelor",

    "mtech": "master",
    "m.tech": "master",
    "me": "master",
    "m.e": "master",
}


def normalize_education(text: str) -> str:
    """
    Normalize education text for easier comparison.
    """

    if not text:
        return ""

    text = text.lower().strip()

    for alias, normalized in DEGREE_ALIASES.items():
        text = text.replace(alias, normalized)

    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def education_matches(
    candidate_education: str,
    required_education: str,
) -> bool:
    """
    Check whether candidate education appears compatible
    with the job education requirement.
    """

    if not candidate_education or not required_education:
        return False

    candidate = normalize_education(candidate_education)
    required = normalize_education(required_education)

    # Direct keyword matching
    candidate_words = set(candidate.split())

    # Common degree requirement
    degree_keywords = {
        "bachelor",
        "master",
        "doctorate",
        "phd",
    }

    required_degrees = candidate_words.intersection(degree_keywords)

    # If job explicitly requires a degree level,
    # candidate should have the same level or higher.
    if "bachelor" in required:
        if "bachelor" in candidate or "master" in candidate or "doctorate" in candidate:
            return True

    if "master" in required:
        if "master" in candidate or "doctorate" in candidate:
            return True

    if "doctorate" in required or "phd" in required:
        if "doctorate" in candidate or "phd" in candidate:
            return True

    # Field matching
    candidate_tokens = set(candidate.split())
    required_tokens = set(required.split())

    field_keywords = {
        "computer",
        "science",
        "data",
        "statistics",
        "mathematics",
        "engineering",
        "analytics",
        "information",
        "technology",
    }

    candidate_fields = candidate_tokens.intersection(field_keywords)
    required_fields = required_tokens.intersection(field_keywords)

    if required_fields and candidate_fields.intersection(required_fields):
        return True

    return False


def calculate_education_score(
    resume: ResumeProfile,
    job: JobProfile,
) -> float:
    """
    Calculate education compatibility score from 0 to 100.
    """

    if not job.education:
        return 100.0

    if not resume.education:
        return 0.0

    required_education = job.education

    best_score = 0.0

    for education in resume.education:

        candidate_text = " ".join(
            [
                education.degree or "",
                education.field or "",
                education.institution or "",
            ]
        )

        if education_matches(candidate_text, required_education):
            best_score = max(best_score, 100.0)

    return round(best_score, 2)


def match_education(
    resume: ResumeProfile,
    job: JobProfile,
) -> dict[str, object]:
    """
    Return detailed education matching information.
    """

    score = calculate_education_score(resume, job)

    matched = score > 0

    return {
        "score": score,
        "required_education": job.education,
        "candidate_education": [
            {
                "degree": education.degree,
                "field": education.field,
                "institution": education.institution,
                "year": education.year,
            }
            for education in resume.education
        ],
        "matched": matched,
    }