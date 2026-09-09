from app.schemas.resume import (ResumeProfile,Experience, Project)
from app.schemas.job import JobProfile

from src.optimization.keyword_optimizer import find_resume_keywords


from src.optimization.bullet_optimizer import (
    optimize_bullet,
    optimize_project_bullet,
)

from src.optimization.summary_optimizer import optimize_summary

from src.optimization.resume_optimizer import optimize_resume

from src.optimization.optimization_pipeline import build_resume_text

from src.optimization.optimization_pipeline import (
    run_optimization_pipeline,
)

def test_keyword_optimizer():
    resume = ResumeProfile(
        candidate_id="candidate_001",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "Pandas",
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "Scikit-learn",
        ],
        preferred_skills=[
            "Docker",
            "AWS",
        ],
    )

    result = find_resume_keywords(resume, job)

    assert "python" in result["matched_required_keywords"]
    assert "sql" in result["matched_required_keywords"]
    assert "machine learning" in result["matched_required_keywords"]

    assert "scikit-learn" in result["missing_required_keywords"]

    assert "docker" in result["missing_preferred_keywords"]
    assert "aws" in result["missing_preferred_keywords"]


def test_optimize_bullet_removes_weak_start():
    result = optimize_bullet(
        "worked on a machine learning project",
        ["Python", "Machine Learning"],
    )

    assert result == "A machine learning project."


def test_optimize_bullet_adds_period():
    result = optimize_bullet(
        "Developed a machine learning model",
        ["Machine Learning"],
    )

    assert result == "Developed a machine learning model."


def test_optimize_project_bullet_preserves_technologies():
    project = Project(
        name="Insurance Cost Prediction",
        description="Built a machine learning model",
        technologies=[
            "Python",
            "Scikit-learn",
            "XGBoost",
        ],
    )

    result = optimize_project_bullet(
        project,
        ["Python", "Machine Learning", "XGBoost"],
    )

    assert "Built a machine learning model" in result
    assert "Python" in result
    assert "Scikit-learn" in result
    assert "XGBoost" in result

def test_summary_optimizer_uses_relevant_skills():
    resume = ResumeProfile(
        candidate_id="candidate_001",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "Pandas",
        ],
        projects=[
            Project(
                name="ML Project",
                description="Built a machine learning model",
                technologies=["Python"],
            )
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
    )

    result = optimize_summary(resume, job)

    assert "Data Scientist" in result
    assert "Python" in result
    assert "SQL" in result
    assert "Machine Learning" in result
    assert "1 project" in result


def test_summary_optimizer_includes_experience():
    resume = ResumeProfile(
        candidate_id="candidate_001",
        skills=["Python", "SQL"],
        experience=[
            Experience(
                company="ABC Technologies",
                role="Data Analyst",
                years=1.5,
            )
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=["Python", "SQL"],
    )

    result = optimize_summary(resume, job)

    assert "1.5+ years of experience" in result
    assert "Python" in result
    assert "SQL" in result


def test_summary_optimizer_does_not_invent_skills():
    resume = ResumeProfile(
        candidate_id="candidate_001",
        skills=["Python", "SQL"],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "TensorFlow",
            "AWS",
        ],
    )

    result = optimize_summary(resume, job)

    assert "Python" in result
    assert "SQL" in result
    assert "TensorFlow" not in result
    assert "AWS" not in result

def test_resume_optimizer_updates_summary():

    resume = ResumeProfile(
        candidate_id="candidate_001",
        summary="Data professional.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
    )

    result = optimize_resume(resume, job)

    optimized = result["optimized_resume"]

    assert optimized.summary is not None
    assert "Data Scientist" in optimized.summary
    assert "Python" in optimized.summary
    assert "SQL" in optimized.summary


def test_resume_optimizer_updates_projects():

    resume = ResumeProfile(
        candidate_id="candidate_001",
        skills=["Python"],
        projects=[
            Project(
                name="ML Project",
                description="worked on machine learning",
                technologies=["Python", "Scikit-learn"],
            )
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=["Python"],
    )

    result = optimize_resume(resume, job)

    optimized = result["optimized_resume"]

    assert len(optimized.projects) == 1

    description = optimized.projects[0].description

    assert description is not None
    assert description[0].isupper()
    assert "Python" in description
    assert "Scikit-learn" in description


def test_resume_optimizer_does_not_invent_skills():

    resume = ResumeProfile(
        candidate_id="candidate_001",
        skills=[
            "Python",
            "SQL",
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "TensorFlow",
            "AWS",
        ],
    )

    result = optimize_resume(resume, job)

    optimized = result["optimized_resume"]

    assert "Python" in optimized.summary
    assert "SQL" in optimized.summary

    assert "TensorFlow" not in optimized.summary
    assert "AWS" not in optimized.summary


def test_resume_optimizer_returns_keyword_analysis():

    resume = ResumeProfile(
        candidate_id="candidate_001",
        skills=[
            "Python",
            "SQL",
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        preferred_skills=[
            "Docker",
        ],
    )

    result = optimize_resume(resume, job)

    keyword_analysis = result["keyword_analysis"]

    assert "python" in keyword_analysis["matched_required_keywords"]
    assert "sql" in keyword_analysis["matched_required_keywords"]

    assert "machine learning" in (
        keyword_analysis["missing_required_keywords"]
    )

    assert "docker" in (
        keyword_analysis["missing_preferred_keywords"]
    )


def test_resume_optimizer_preserves_candidate_id():

    resume = ResumeProfile(
        candidate_id="candidate_001",
        skills=["Python"],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=["Python"],
    )

    result = optimize_resume(resume, job)

    optimized = result["optimized_resume"]

    assert optimized.candidate_id == "candidate_001"

def test_build_resume_text_contains_resume_information():

    resume = ResumeProfile(
        candidate_id="candidate_001",
        name="John Doe",
        summary="Data professional.",
        skills=["Python", "SQL"],
        projects=[
            Project(
                name="ML Project",
                description="Built a machine learning model.",
                technologies=["Python", "Scikit-learn"],
            )
        ],
    )

    text = build_resume_text(resume)

    assert "John Doe" in text
    assert "Data professional." in text
    assert "Python" in text
    assert "SQL" in text
    assert "ML Project" in text
    assert "Scikit-learn" in text

def test_optimization_is_rejected_when_score_decreases():
    resume = ResumeProfile(
        candidate_id="candidate_001",
        summary="Data professional.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        projects=[
            Project(
                name="ML Project",
                description="worked on machine learning",
                technologies=[
                    "Python",
                    "Scikit-learn",
                ],
            )
        ],
    )

    job = JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        preferred_skills=[
            "Docker",
            "AWS",
        ],
    )

    result = run_optimization_pipeline(
        resume=resume,
        job=job,
        resume_text=(
            "Python SQL Machine Learning "
            "worked on machine learning"
        ),
        job_text=(
            "Data Scientist Python SQL Machine Learning "
            "Docker AWS"
        ),
    )

    assert result["optimized_match"]["overall_score"] < (
        result["initial_match"]["overall_score"]
    )

    assert result["optimization_accepted"] is False

    assert (
        result["final_match"]["overall_score"]
        == result["initial_match"]["overall_score"]
    )

    assert result["final_resume_text"] == (
        "Python SQL Machine Learning worked on machine learning"
    )