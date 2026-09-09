from app.schemas.resume import ResumeProfile
from app.schemas.job import JobProfile


def calculate_total_experience(resume: ResumeProfile) -> float:
    """
    Calculate total years of professional experience from the resume.
    """
    if not resume.experience:
        return 0.0

    total_years = sum(
        experience.years
        for experience in resume.experience
        if experience.years > 0
    )

    return round(total_years, 2)


def calculate_experience_score(
    candidate_experience: float,
    required_experience: float,
) -> float:
    """
    Compare candidate experience against the job requirement.

    Rules:
    - No requirement -> 100
    - No candidate experience -> 0
    - Candidate meets/exceeds requirement -> 100
    - Partial experience -> proportional score
    """
    if required_experience <= 0:
        return 100.0

    if candidate_experience <= 0:
        return 0.0

    if candidate_experience >= required_experience:
        return 100.0

    score = (candidate_experience / required_experience) * 100

    return round(score, 2)


def match_experience(
    resume: ResumeProfile,
    job: JobProfile,
) -> dict[str, object]:
    """
    Calculate candidate experience and compare it with the job requirement.
    """
    candidate_experience = calculate_total_experience(resume)

    required_experience = job.minimum_experience

    score = calculate_experience_score(
        candidate_experience=candidate_experience,
        required_experience=required_experience,
    )

    return {
        "candidate_experience": candidate_experience,
        "required_experience": required_experience,
        "score": score,
        "meets_requirement": candidate_experience >= required_experience,
    }