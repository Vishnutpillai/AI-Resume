from app.schemas.resume import ResumeProfile
from app.schemas.job import JobProfile
from src.matching.skill_matcher import normalize_skill


def calculate_project_score(
    resume: ResumeProfile,
    job: JobProfile,
) -> float:
    """
    Calculate project relevance based on technology overlap
    with the job's required and preferred skills.
    """

    if not resume.projects:
        return 0.0

    job_skills = {
        normalize_skill(skill)
        for skill in (
            job.required_skills + job.preferred_skills
        )
        if normalize_skill(skill)
    }

    if not job_skills:
        return 0.0

    project_scores = []

    for project in resume.projects:
        project_skills = {
            normalize_skill(skill)
            for skill in project.technologies
            if normalize_skill(skill)
        }

        # Also consider project description.
        description = (project.description or "").lower()

        for skill in job_skills:
            if skill in description:
                project_skills.add(skill)

        if project_skills:
            matched = project_skills.intersection(job_skills)
            score = (len(matched) / len(job_skills)) * 100
        else:
            score = 0.0

        project_scores.append(score)

    return round(max(project_scores), 2)


def match_projects(
    resume: ResumeProfile,
    job: JobProfile,
) -> dict[str, object]:
    """
    Return project relevance information.
    """

    score = calculate_project_score(resume, job)

    relevant_projects = []

    job_skills = {
        normalize_skill(skill)
        for skill in (
            job.required_skills + job.preferred_skills
        )
        if normalize_skill(skill)
    }

    for project in resume.projects:
        project_text = " ".join(
            [
                project.name or "",
                project.description or "",
                " ".join(project.technologies),
            ]
        ).lower()

        matched_skills = sorted(
            skill
            for skill in job_skills
            if skill in project_text
        )

        if matched_skills:
            relevant_projects.append(
                {
                    "name": project.name,
                    "matched_skills": matched_skills,
                }
            )

    return {
        "score": score,
        "relevant_projects": relevant_projects,
        "project_count": len(resume.projects),
    }