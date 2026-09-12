from app.schemas.job import JobProfile
from app.schemas.resume import (
    Education,
    Experience,
    Project,
    ResumeProfile,
)
from src.agents.evaluation_agent import EvaluationAgent


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


def test_evaluation_agent_evaluate():
    agent = EvaluationAgent()

    result = agent.evaluate(
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
    assert 0 <= result["overall_match_score"] <= 100


def test_evaluation_agent_contains_match_breakdown():
    agent = EvaluationAgent()

    result = agent.evaluate(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    assert result["match_breakdown"] is not None


def test_evaluation_agent_contains_ats_analysis():
    agent = EvaluationAgent()

    result = agent.evaluate(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    assert result["ats_analysis"] is not None


def test_evaluation_agent_contains_skill_gaps():
    agent = EvaluationAgent()

    result = agent.evaluate(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    assert result["skill_gap_analysis"] is not None


def test_evaluation_agent_contains_recommendations():
    agent = EvaluationAgent()

    result = agent.evaluate(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    assert isinstance(result["recommendations"], list)


def test_evaluation_agent_requires_resume():
    agent = EvaluationAgent()

    try:
        agent.evaluate(
            resume=None,
            job=sample_job(),
            resume_text="Python",
            job_text="Python",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_evaluation_agent_requires_job():
    agent = EvaluationAgent()

    try:
        agent.evaluate(
            resume=sample_resume(),
            job=None,
            resume_text="Python",
            job_text="Python",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_evaluation_agent_requires_rag_for_evidence():
    agent = EvaluationAgent()

    try:
        agent.retrieve_relevant_evidence(
            "Python machine learning"
        )
        assert False, "Expected RuntimeError"
    except RuntimeError:
        pass