from typing import Any

from app.schemas.resume import ResumeProfile
from app.schemas.job import JobProfile

from src.matching.scoring_engine import calculate_match_result
from src.evaluation.ats_analyzer import analyze_ats
from src.evaluation.skill_gap_analyzer import analyze_skill_gaps
from src.evaluation.score_comparator import compare_scores
from src.optimization.resume_optimizer import optimize_resume


def build_resume_text(resume: ResumeProfile) -> str:
    """
    Convert a structured ResumeProfile into searchable resume text.

    Only information already present in the ResumeProfile is included.
    This text is used for semantic matching after optimization.
    """

    sections: list[str] = []

    if resume.name:
        sections.append(resume.name)

    if resume.summary:
        sections.append("SUMMARY")
        sections.append(resume.summary)

    if resume.skills:
        sections.append("SKILLS")
        sections.append(", ".join(resume.skills))

    if resume.experience:
        sections.append("EXPERIENCE")

        for experience in resume.experience:
            experience_text = []

            if experience.role:
                experience_text.append(experience.role)

            if experience.company:
                experience_text.append(experience.company)

            if experience.years:
                experience_text.append(
                    f"{experience.years:g} years experience"
                )

            if experience_text:
                sections.append(" | ".join(experience_text))

    if resume.projects:
        sections.append("PROJECTS")

        for project in resume.projects:
            project_text = []

            if project.name:
                project_text.append(project.name)

            if project.description:
                project_text.append(project.description)

            if project.technologies:
                project_text.append(
                    "Technologies: "
                    + ", ".join(project.technologies)
                )

            if project_text:
                sections.append(" | ".join(project_text))

    if resume.education:
        sections.append("EDUCATION")

        for education in resume.education:
            education_text = []

            if education.degree:
                education_text.append(education.degree)

            if education.field:
                education_text.append(education.field)

            if education.institution:
                education_text.append(education.institution)

            if education.year:
                education_text.append(str(education.year))

            if education_text:
                sections.append(" | ".join(education_text))

    if resume.certifications:
        sections.append("CERTIFICATIONS")
        sections.append(", ".join(resume.certifications))

    return "\n".join(sections)


def run_optimization_pipeline(
    resume: ResumeProfile,
    job: JobProfile,
    resume_text: str,
    job_text: str,
) -> dict[str, Any]:
    """
    Run the complete resume optimization workflow.

    Workflow:

    1. Calculate initial match score
    2. Analyze ATS compatibility
    3. Analyze skill gaps
    4. Generate optimized resume
    5. Rebuild optimized resume text
    6. Recalculate match score
    7. Compare before vs after
    8. Accept optimization only if score does not decrease

    The optimizer never invents unsupported qualifications.
    """

    # ---------------------------------------------------------
    # 1. Initial match
    # ---------------------------------------------------------

    initial_match = calculate_match_result(
        resume=resume,
        job=job,
        resume_text=resume_text,
        job_text=job_text,
    )

    # ---------------------------------------------------------
    # 2. ATS analysis
    # ---------------------------------------------------------

    ats_result = analyze_ats(
        resume=resume,
        job=job,
        resume_text=resume_text,
    )

    # ---------------------------------------------------------
    # 3. Skill-gap analysis
    # ---------------------------------------------------------

    skill_gap_result = analyze_skill_gaps(
        resume=resume,
        job=job,
    )

    # ---------------------------------------------------------
    # 4. Generate optimization
    # ---------------------------------------------------------

    optimization_result = optimize_resume(
        resume=resume,
        job=job,
    )

    optimized_resume = optimization_result["optimized_resume"]

    if not isinstance(optimized_resume, ResumeProfile):
        raise TypeError(
            "optimize_resume() must return a ResumeProfile "
            "under the 'optimized_resume' key."
        )

    # ---------------------------------------------------------
    # 5. Rebuild optimized resume text
    # ---------------------------------------------------------

    optimized_resume_text = build_resume_text(
        optimized_resume
    )

    # ---------------------------------------------------------
    # 6. Recalculate using SAME scoring engine
    # ---------------------------------------------------------

    optimized_match = calculate_match_result(
        resume=optimized_resume,
        job=job,
        resume_text=optimized_resume_text,
        job_text=job_text,
    )

    # ---------------------------------------------------------
    # 7. Compare scores
    # ---------------------------------------------------------

    comparison = compare_scores(
        before=initial_match,
        after=optimized_match,
    )

    # ---------------------------------------------------------
    # 8. Optimization acceptance gate
    # ---------------------------------------------------------

    optimization_accepted = (
        optimized_match["overall_score"]
        >= initial_match["overall_score"]
    )

    if optimization_accepted:
        final_resume = optimized_resume
        final_resume_text = optimized_resume_text
        final_match = optimized_match
    else:
        final_resume = resume
        final_resume_text = resume_text
        final_match = initial_match

        optimization_result["suggestions"].append(
            "Generated optimization was rejected because "
            "it reduced the overall match score."
        )

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    return {
        "initial_match": initial_match,
        "ats_analysis": ats_result,
        "skill_gap_analysis": skill_gap_result,
        "optimization": optimization_result,

        "optimized_resume": optimized_resume.model_dump(),
        "optimized_resume_text": optimized_resume_text,
        "optimized_match": optimized_match,

        "optimization_accepted": optimization_accepted,

        "final_resume": final_resume.model_dump(),
        "final_resume_text": final_resume_text,
        "final_match": final_match,

        "comparison": comparison,
    }