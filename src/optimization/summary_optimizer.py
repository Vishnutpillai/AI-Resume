from app.schemas.resume import ResumeProfile
from app.schemas.job import JobProfile
from src.matching.skill_matcher import normalize_skill


def optimize_summary(
    resume: ResumeProfile,
    job: JobProfile,
) -> str:
    """
    Generate an evidence-grounded, job-focused professional summary.

    Only information already present in the resume is used.
    No unsupported skills, experience, achievements, certifications,
    or metrics are introduced.
    """

    skills = [
        skill.strip()
        for skill in resume.skills
        if skill.strip() and normalize_skill(skill)
    ]

    required_skills = {
        normalize_skill(skill)
        for skill in job.required_skills
        if normalize_skill(skill)
    }

    preferred_skills = {
        normalize_skill(skill)
        for skill in job.preferred_skills
        if normalize_skill(skill)
    }

    relevant_skills = []

    for skill in skills:
        normalized = normalize_skill(skill)

        if (
            normalized in required_skills
            or normalized in preferred_skills
        ):
            relevant_skills.append(skill)

    if not relevant_skills:
        relevant_skills = skills[:5]

    total_experience = sum(
        experience.years
        for experience in resume.experience
    )

    project_count = len(resume.projects)

    role = job.title.strip()

    # Build experience statement.
    if total_experience > 0:
        experience_text = (
            f"{total_experience:g}+ years of experience"
        )
    else:
        experience_text = "hands-on project experience"

    # Build skill statement.
    skill_text = ", ".join(relevant_skills[:6])

    summary = (
        f"Professional targeting {role}, "
        f"with {experience_text}"
    )

    if skill_text:
        summary += f" in {skill_text}"

    summary += "."

    if project_count:
        project_word = "project" if project_count == 1 else "projects"

        summary += (
            f" Demonstrated practical application through "
            f"{project_count} {project_word}."
        )

    return summary
