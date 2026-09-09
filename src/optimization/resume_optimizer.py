from copy import deepcopy

from app.schemas.resume import ResumeProfile
from app.schemas.job import JobProfile

from src.optimization.keyword_optimizer import find_resume_keywords
from src.optimization.summary_optimizer import optimize_summary
from src.optimization.bullet_optimizer import optimize_project_bullet


def optimize_resume(
    resume: ResumeProfile,
    job: JobProfile,
) -> dict[str, object]:
    """
    Deterministic resume optimization.

    Only uses information already present in the resume.
    It does not invent skills, experience, certifications,
    achievements, or metrics.
    """

    optimized_resume = deepcopy(resume)

    # ---------------------------------------------------------
    # 1. Identify relevant and missing keywords
    # ---------------------------------------------------------
    keyword_analysis = find_resume_keywords(resume, job)

    relevant_keywords = (
        keyword_analysis["matched_required_keywords"]
        + keyword_analysis["matched_preferred_keywords"]
    )

    # ---------------------------------------------------------
    # 2. Optimize summary
    # ---------------------------------------------------------
    optimized_resume.summary = optimize_summary(
        resume,
        job,
    )

    # ---------------------------------------------------------
    # 3. Optimize project descriptions
    # ---------------------------------------------------------
    optimized_projects = []

    for project in resume.projects:
        optimized_project = deepcopy(project)

        optimized_project.description = optimize_project_bullet(
            project,
            relevant_keywords,
        )

        optimized_projects.append(optimized_project)

    optimized_resume.projects = optimized_projects

    # ---------------------------------------------------------
    # 4. Generate optimization suggestions
    # ---------------------------------------------------------
    suggestions = []

    if keyword_analysis["missing_required_keywords"]:
        suggestions.append(
            "Consider adding missing required keywords only "
            "if they are genuinely supported by your experience."
        )

    if keyword_analysis["missing_preferred_keywords"]:
        suggestions.append(
            "Consider adding preferred skills only when you "
            "have genuine practical exposure to them."
        )

    if resume.summary:
        suggestions.append(
            "Resume summary was rewritten to emphasize skills "
            "relevant to the target job."
        )
    else:
        suggestions.append(
            "A job-focused summary was generated from existing "
            "resume information."
        )

    if resume.projects:
        suggestions.append(
            "Project descriptions were strengthened using "
            "technologies already listed in the resume."
        )

    return {
        "optimized_resume": optimized_resume,
        "keyword_analysis": keyword_analysis,
        "suggestions": suggestions,
    }