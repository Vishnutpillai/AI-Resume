from app.schemas.job import JobProfile
from app.schemas.resume import (
    Education,
    Experience,
    Project,
    ResumeProfile,
)
from src.agents.matching_agent import MatchingAgent


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


def test_matching_agent_analyze():
    agent = MatchingAgent()

    result = agent.analyze(
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
    assert 0 <= result["overall_score"] <= 100


def test_matching_agent_contains_breakdown():
    agent = MatchingAgent()

    result = agent.analyze(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    breakdown = result["breakdown"]

    assert "required_skill_score" in breakdown
    assert "semantic_score" in breakdown
    assert "experience_score" in breakdown


def test_matching_agent_contains_skill_match():
    agent = MatchingAgent()

    result = agent.analyze(
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL machine learning",
        job_text="Python SQL machine learning",
    )

    assert result["skill_match"] is not None
    assert "Python" in result["skill_match"]["matched"]
    assert "SQL" in result["skill_match"]["matched"]


def test_matching_agent_requires_resume():
    agent = MatchingAgent()

    try:
        agent.analyze(
            resume=None,
            job=sample_job(),
            resume_text="Python",
            job_text="Python",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_matching_agent_requires_job():
    agent = MatchingAgent()

    try:
        agent.analyze(
            resume=sample_resume(),
            job=None,
            resume_text="Python",
            job_text="Python",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_matching_agent_requires_resume_text():
    agent = MatchingAgent()

    try:
        agent.analyze(
            resume=sample_resume(),
            job=sample_job(),
            resume_text="",
            job_text="Python",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_matching_agent_requires_job_text():
    agent = MatchingAgent()

    try:
        agent.analyze(
            resume=sample_resume(),
            job=sample_job(),
            resume_text="Python",
            job_text="",
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_matching_agent_requires_rag_for_evidence():
    agent = MatchingAgent()

    try:
        agent.retrieve_relevant_evidence(
            "Python machine learning"
        )
        assert False, "Expected RuntimeError"
    except RuntimeError:
        pass
    