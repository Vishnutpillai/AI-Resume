from app.schemas.resume import ResumeProfile
from app.schemas.job import JobProfile
from src.matching.skill_matcher import match_required_and_preferred_skills
from src.matching.semantic_matcher import calculate_semantic_score
from src.matching.experience_matcher import match_experience
from src.matching.project_matcher import match_projects
from src.matching.education_matcher import match_education


REQUIRED_SKILLS_WEIGHT = 0.30
SEMANTIC_WEIGHT = 0.25
EXPERIENCE_WEIGHT = 0.15
PROJECT_WEIGHT = 0.10
EDUCATION_WEIGHT = 0.10
PREFERRED_SKILLS_WEIGHT = 0.10


def calculate_overall_score(
    required_skill_score: float,
    semantic_score: float,
    experience_score: float,
    project_score: float,
    education_score: float,
    preferred_skill_score: float,
) -> float:
    """
    Calculate the weighted overall resume-job matching score.
    """

    score = (
        required_skill_score * REQUIRED_SKILLS_WEIGHT
        + semantic_score * SEMANTIC_WEIGHT
        + experience_score * EXPERIENCE_WEIGHT
        + project_score * PROJECT_WEIGHT
        + education_score * EDUCATION_WEIGHT
        + preferred_skill_score * PREFERRED_SKILLS_WEIGHT
    )

    return round(score, 2)


def calculate_match_result(
    resume: ResumeProfile,
    job: JobProfile,
    resume_text: str,
    job_text: str,
) -> dict[str, object]:

    # -----------------------------
    # Skill Matching
    # -----------------------------

    skill_result = match_required_and_preferred_skills(
        resume,
        job,
    )

    required_skill_score = skill_result["required"]["score"]
    preferred_skill_score = skill_result["preferred"]["score"]

    # -----------------------------
    # Semantic Matching
    # -----------------------------

    semantic_score = calculate_semantic_score(
        resume_text,
        job_text,
    )

    # -----------------------------
    # Experience Matching
    # -----------------------------

    experience_result = match_experience(
        resume,
        job,
    )

    experience_score = experience_result["score"]

    # -----------------------------
    # Project Matching
    # -----------------------------

    project_result = match_projects(
        resume,
        job,
    )

    project_score = project_result["score"]

    # -----------------------------
    # Education Matching
    # -----------------------------

    education_result = match_education(
        resume,
        job,
    )

    education_score = education_result["score"]

    # -----------------------------
    # Overall Score
    # -----------------------------

    overall_score = calculate_overall_score(
        required_skill_score=required_skill_score,
        semantic_score=semantic_score,
        experience_score=experience_score,
        project_score=project_score,
        education_score=education_score,
        preferred_skill_score=preferred_skill_score,
    )

    # -----------------------------
    # Strengths
    # -----------------------------

    strengths = []

    if required_skill_score >= 80:
        strengths.append(
            "Strong coverage of required technical skills."
        )

    if preferred_skill_score >= 60:
        strengths.append(
            "Good coverage of preferred skills."
        )

    if experience_result["meets_requirement"]:
        strengths.append(
            "Candidate meets the minimum experience requirement."
        )

    if project_score >= 60:
        strengths.append(
            "Projects demonstrate relevant technical experience."
        )

    if education_score >= 80:
        strengths.append(
            "Education is aligned with the job requirement."
        )

    # -----------------------------
    # Weaknesses
    # -----------------------------

    weaknesses = []

    if required_skill_score < 80:
        weaknesses.append(
            "Some required skills are missing."
        )

    if preferred_skill_score < 60:
        weaknesses.append(
            "Several preferred skills are missing."
        )

    if not experience_result["meets_requirement"]:
        weaknesses.append(
            "Candidate does not meet the minimum experience requirement."
        )

    if project_score < 60:
        weaknesses.append(
            "Projects have limited alignment with the job requirements."
        )

    if education_score < 80:
        weaknesses.append(
            "Education has limited alignment with the job requirement."
        )

    # -----------------------------
    # Recommendations
    # -----------------------------

    recommendations = []

    missing_required = skill_result["required"]["missing"]

    if missing_required:
        recommendations.append(
            "Consider highlighting relevant experience with: "
            + ", ".join(missing_required)
            + "."
        )

    missing_preferred = skill_result["preferred"]["missing"]

    if missing_preferred:
        recommendations.append(
            "Consider strengthening exposure to preferred skills: "
            + ", ".join(missing_preferred)
            + "."
        )

    if project_score < 60:
        recommendations.append(
            "Add or emphasize projects that directly match the job requirements."
        )

    if semantic_score < 60:
        recommendations.append(
            "Improve resume wording and job-specific keyword alignment."
        )

    return {
        "candidate_id": resume.candidate_id,
        "job_id": job.job_id,
        "overall_score": overall_score,

        "breakdown": {
            "required_skill_score": required_skill_score,
            "semantic_score": semantic_score,
            "experience_score": experience_score,
            "project_score": project_score,
            "education_score": education_score,
            "preferred_skill_score": preferred_skill_score,
        },

        "skill_match": {
            "matched": skill_result["required"]["matched"],
            "missing": skill_result["required"]["missing"],
        },

        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
    }