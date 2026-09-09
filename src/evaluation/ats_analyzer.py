import re

from app.schemas.resume import ResumeProfile
from app.schemas.job import JobProfile
from src.matching.skill_matcher import normalize_skill


EXPECTED_SECTIONS = {
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
}


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def calculate_keyword_coverage(
    resume_text: str,
    job: JobProfile,
) -> dict[str, object]:

    resume_text_normalized = normalize_text(resume_text)

    required_keywords = {
        normalize_skill(skill)
        for skill in job.required_skills
        if normalize_skill(skill)
    }

    preferred_keywords = {
        normalize_skill(skill)
        for skill in job.preferred_skills
        if normalize_skill(skill)
    }

    all_keywords = required_keywords.union(preferred_keywords)

    matched_keywords = sorted(
        keyword
        for keyword in all_keywords
        if keyword in resume_text_normalized
    )

    missing_keywords = sorted(
        keyword
        for keyword in all_keywords
        if keyword not in resume_text_normalized
    )

    required_matched = sorted(
        keyword
        for keyword in required_keywords
        if keyword in resume_text_normalized
    )

    preferred_matched = sorted(
        keyword
        for keyword in preferred_keywords
        if keyword in resume_text_normalized
    )

    required_coverage = (
        len(required_matched) / len(required_keywords) * 100
        if required_keywords
        else 100.0
    )

    preferred_coverage = (
        len(preferred_matched) / len(preferred_keywords) * 100
        if preferred_keywords
        else 100.0
    )

    overall_coverage = (
        len(matched_keywords) / len(all_keywords) * 100
        if all_keywords
        else 100.0
    )

    return {
        "overall_coverage": round(overall_coverage, 2),
        "required_coverage": round(required_coverage, 2),
        "preferred_coverage": round(preferred_coverage, 2),
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
    }


def analyze_sections(resume: ResumeProfile) -> dict[str, object]:

    sections = {
        "summary": bool(resume.summary),
        "skills": bool(resume.skills),
        "experience": bool(resume.experience),
        "projects": bool(resume.projects),
        "education": bool(resume.education),
    }

    present_sections = [
        section
        for section, exists in sections.items()
        if exists
    ]

    missing_sections = [
        section
        for section, exists in sections.items()
        if not exists
    ]

    score = (
        len(present_sections) / len(EXPECTED_SECTIONS) * 100
        if EXPECTED_SECTIONS
        else 100.0
    )

    return {
        "score": round(score, 2),
        "present_sections": present_sections,
        "missing_sections": missing_sections,
    }


def analyze_title_relevance(
    resume: ResumeProfile,
    job: JobProfile,
) -> dict[str, object]:

    resume_summary = normalize_text(resume.summary or "")
    job_title = normalize_text(job.title)

    if not job_title:
        return {
            "score": 100.0,
            "matched": True,
        }

    title_words = {
        word
        for word in job_title.split()
        if len(word) > 2
    }

    matched_words = [
        word
        for word in title_words
        if word in resume_summary
    ]

    if not title_words:
        score = 100.0
    else:
        score = len(matched_words) / len(title_words) * 100

    return {
        "score": round(score, 2),
        "matched": bool(matched_words),
        "matched_words": sorted(matched_words),
    }


def analyze_project_strength(
    resume: ResumeProfile,
    job: JobProfile,
) -> dict[str, object]:

    if not resume.projects:
        return {
            "score": 0.0,
            "project_count": 0,
            "strong_projects": [],
        }

    job_keywords = {
        normalize_skill(skill)
        for skill in (
            job.required_skills
            + job.preferred_skills
            + job.keywords
        )
        if normalize_skill(skill)
    }

    strong_projects = []

    for project in resume.projects:

        project_text = normalize_text(
            " ".join(
                [
                    project.name or "",
                    project.description or "",
                    " ".join(project.technologies),
                ]
            )
        )

        matched_keywords = [
            keyword
            for keyword in job_keywords
            if keyword in project_text
        ]

        if matched_keywords:
            strong_projects.append(
                {
                    "name": project.name,
                    "matched_keywords": sorted(set(matched_keywords)),
                }
            )

    score = (
        len(strong_projects) / len(resume.projects) * 100
    )

    return {
        "score": round(score, 2),
        "project_count": len(resume.projects),
        "strong_projects": strong_projects,
    }


def analyze_metrics(resume_text: str) -> dict[str, object]:

    if not resume_text:
        return {
            "score": 0.0,
            "metric_count": 0,
            "has_metrics": False,
        }

    # Detect common quantitative evidence:
    # 94%, 18%, 2 years, 100K, 10+, etc.
    metric_patterns = [
        r"\b\d+%",
        r"\b\d+\+",
        r"\b\d+\s*(?:years?|months?)\b",
        r"\b\d+(?:,\d{3})+\b",
        r"\b\d+(?:\.\d+)?[kKmMbB]\b",
    ]

    matches = []

    for pattern in metric_patterns:
        matches.extend(
            re.findall(pattern, resume_text)
        )

    metric_count = len(matches)

    if metric_count >= 3:
        score = 100.0
    elif metric_count == 2:
        score = 75.0
    elif metric_count == 1:
        score = 50.0
    else:
        score = 0.0

    return {
        "score": score,
        "metric_count": metric_count,
        "has_metrics": metric_count > 0,
    }


def analyze_formatting(resume_text: str) -> dict[str, object]:

    if not resume_text:
        return {
            "score": 0.0,
            "issues": ["Resume text is empty."],
        }

    issues = []

    lines = resume_text.splitlines()

    if len(lines) < 10:
        issues.append("Resume appears too short.")

    if len(resume_text) > 15000:
        issues.append("Resume may contain excessive content.")

    # Detect unusual excessive special characters.
    special_characters = len(
        re.findall(r"[^\w\s.,;:()/%+\-]", resume_text)
    )

    if special_characters > 100:
        issues.append(
            "Resume contains many special characters."
        )

    score = max(
        0.0,
        100.0 - (len(issues) * 20.0),
    )

    return {
        "score": round(score, 2),
        "issues": issues,
    }


def calculate_ats_score(
    keyword_score: float,
    section_score: float,
    title_score: float,
    project_score: float,
    metric_score: float,
    formatting_score: float,
) -> float:

    score = (
        keyword_score * 0.35
        + section_score * 0.15
        + title_score * 0.10
        + project_score * 0.15
        + metric_score * 0.15
        + formatting_score * 0.10
    )

    return round(score, 2)


def analyze_ats(
    resume: ResumeProfile,
    job: JobProfile,
    resume_text: str,
) -> dict[str, object]:

    keyword_result = calculate_keyword_coverage(
        resume_text,
        job,
    )

    section_result = analyze_sections(resume)

    title_result = analyze_title_relevance(
        resume,
        job,
    )

    project_result = analyze_project_strength(
        resume,
        job,
    )

    metric_result = analyze_metrics(
        resume_text,
    )

    formatting_result = analyze_formatting(
        resume_text,
    )

    ats_score = calculate_ats_score(
        keyword_score=keyword_result["overall_coverage"],
        section_score=section_result["score"],
        title_score=title_result["score"],
        project_score=project_result["score"],
        metric_score=metric_result["score"],
        formatting_score=formatting_result["score"],
    )

    recommendations = []

    if keyword_result["missing_keywords"]:
        recommendations.append(
            "Consider naturally incorporating missing job keywords "
            "when they are genuinely supported by the candidate's experience."
        )

    if section_result["missing_sections"]:
        recommendations.append(
            "Consider adding missing resume sections: "
            + ", ".join(section_result["missing_sections"])
            + "."
        )

    if title_result["score"] < 50:
        recommendations.append(
            "Improve alignment between the resume summary and target job title."
        )

    if project_result["score"] < 60:
        recommendations.append(
            "Strengthen projects by highlighting technologies and responsibilities "
            "relevant to the target job."
        )

    if metric_result["score"] < 50:
        recommendations.append(
            "Add measurable achievements where they are factually available."
        )

    if formatting_result["issues"]:
        recommendations.append(
            "Review resume formatting for ATS compatibility."
        )

    return {
        "ats_score": ats_score,
        "keyword_analysis": keyword_result,
        "section_analysis": section_result,
        "title_analysis": title_result,
        "project_analysis": project_result,
        "metric_analysis": metric_result,
        "formatting_analysis": formatting_result,
        "recommendations": recommendations,
    }