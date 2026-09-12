from app.schemas.job import JobProfile
from app.schemas.resume import (
    Education,
    Experience,
    Project,
    ResumeProfile,
)
from src.agents.orchestrator import AgentOrchestrator


def sample_resume() -> ResumeProfile:
    return ResumeProfile(
        candidate_id="candidate_001",
        name="Test Candidate",
        summary="Data Scientist with Python and SQL experience.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "Pandas",
        ],
        experience=[
            Experience(
                company="ABC Technologies",
                role="Data Scientist",
                years=1.5,
            )
        ],
        projects=[
            Project(
                name="Churn Prediction",
                description=(
                    "Built a machine learning prediction model "
                    "using Python and scikit-learn."
                ),
                technologies=[
                    "Python",
                    "Scikit-learn",
                ],
            )
        ],
        education=[
            Education(
                degree="Bachelor's Degree",
                field="Computer Science",
                institution="Test University",
                year=2024,
            )
        ],
    )


def sample_job() -> JobProfile:
    return JobProfile(
        job_id="job_001",
        title="Data Scientist",
        company="ABC Technologies",
        description=(
            "Develop machine learning models and predictive "
            "solutions using Python and SQL."
        ),
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        preferred_skills=[
            "Docker",
            "AWS",
        ],
        minimum_experience=1.0,
        education="Bachelor's degree in Computer Science",
        keywords=[
            "Data Scientist",
            "Python",
            "Machine Learning",
        ],
    )


def test_orchestrator_run():
    orchestrator = AgentOrchestrator()

    result = orchestrator.run(
        resume=sample_resume(),
        job=sample_job(),
        resume_text=(
            "Data Scientist Python SQL Machine Learning Pandas "
            "Churn Prediction scikit-learn"
        ),
        job_text=(
            "Data Scientist Python SQL Machine Learning "
            "predictive solutions"
        ),
    )

    assert result["candidate_id"] == "candidate_001"
    assert result["job_id"] == "job_001"


def test_orchestrator_contains_all_agent_outputs():
    orchestrator = AgentOrchestrator()

    result = orchestrator.run(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    assert result["resume_analysis"] is not None
    assert result["jd_analysis"] is not None
    assert result["skill_analysis"] is not None
    assert result["matching_analysis"] is not None
    assert result["evaluation_analysis"] is not None


def test_orchestrator_resume_analysis():
    orchestrator = AgentOrchestrator()

    result = orchestrator.run(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    assert result["resume_analysis"]["candidate_id"] == "candidate_001"


def test_orchestrator_jd_analysis():
    orchestrator = AgentOrchestrator()

    result = orchestrator.run(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    assert result["jd_analysis"]["job_id"] == "job_001"


def test_orchestrator_skill_analysis():
    orchestrator = AgentOrchestrator()

    result = orchestrator.run(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    assert "Python" in result["skill_analysis"]["matched_required_skills"]


def test_orchestrator_matching_analysis():
    orchestrator = AgentOrchestrator()

    result = orchestrator.run(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    assert 0 <= result["matching_analysis"]["overall_score"] <= 100


def test_orchestrator_evaluation_analysis():
    orchestrator = AgentOrchestrator()

    result = orchestrator.run(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    assert result["evaluation_analysis"]["overall_match_score"] >= 0


def test_orchestrator_requires_resume():
    orchestrator = AgentOrchestrator()

    try:
        orchestrator.run(
            resume=None,
            job=sample_job(),
            resume_text="Python",
            job_text="Python",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_orchestrator_requires_job():
    orchestrator = AgentOrchestrator()

    try:
        orchestrator.run(
            resume=sample_resume(),
            job=None,
            resume_text="Python",
            job_text="Python",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass