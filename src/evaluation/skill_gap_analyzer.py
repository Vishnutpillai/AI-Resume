from app.schemas.resume import ResumeProfile
from app.schemas.job import JobProfile
from src.matching.skill_matcher import normalize_skill


def normalize_skill_set(skills: list[str]) -> set[str]:
    return {
        normalize_skill(skill)
        for skill in skills
        if normalize_skill(skill)
    }


def analyze_skill_gaps(
    resume: ResumeProfile,
    job: JobProfile,
) -> dict[str, object]:

    resume_skills = normalize_skill_set(resume.skills)

    required_skills = normalize_skill_set(
        job.required_skills
    )

    preferred_skills = normalize_skill_set(
        job.preferred_skills
    )

    matched_required = sorted(
        resume_skills.intersection(required_skills)
    )

    missing_required = sorted(
        required_skills - resume_skills
    )

    matched_preferred = sorted(
        resume_skills.intersection(preferred_skills)
    )

    missing_preferred = sorted(
        preferred_skills - resume_skills
    )

    gaps = []

    for skill in missing_required:
        gaps.append(
            {
                "skill": skill,
                "category": "required",
                "priority": "high",
                "recommendation": (
                    f"Develop practical experience with {skill} "
                    "and demonstrate it through a project or relevant work."
                ),
            }
        )

    for skill in missing_preferred:
        gaps.append(
            {
                "skill": skill,
                "category": "preferred",
                "priority": "medium",
                "recommendation": (
                    f"Consider learning or gaining practical exposure "
                    f"to {skill} if relevant to your target role."
                ),
            }
        )

    if missing_required:
        learning_path = [
            {
                "priority": "high",
                "focus": "Required Skills",
                "skills": missing_required,
                "action": (
                    "Prioritize these skills because they are explicitly "
                    "required by the job description."
                ),
            }
        ]
    else:
        learning_path = []

    if missing_preferred:
        learning_path.append(
            {
                "priority": "medium",
                "focus": "Preferred Skills",
                "skills": missing_preferred,
                "action": (
                    "Strengthen these skills after addressing required "
                    "skill gaps."
                ),
            }
        )

    if not missing_required and not missing_preferred:
        learning_path.append(
            {
                "priority": "low",
                "focus": "Skill Maintenance",
                "skills": [],
                "action": (
                    "Continue strengthening existing skills through "
                    "projects and practical experience."
                ),
            }
        )

    total_required = len(required_skills)

    required_coverage = (
        len(matched_required) / total_required * 100
        if total_required
        else 100.0
    )

    total_preferred = len(preferred_skills)

    preferred_coverage = (
        len(matched_preferred) / total_preferred * 100
        if total_preferred
        else 100.0
    )

    return {
        "matched_required": matched_required,
        "missing_required": missing_required,
        "matched_preferred": matched_preferred,
        "missing_preferred": missing_preferred,
        "required_coverage": round(required_coverage, 2),
        "preferred_coverage": round(preferred_coverage, 2),
        "gaps": gaps,
        "learning_path": learning_path,
    }