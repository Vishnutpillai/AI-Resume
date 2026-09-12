from app.schemas.resume import (
    Education,
    Experience,
    Project,
    ResumeProfile,
)
from src.agents.resume_agent import ResumeAgent


def sample_resume() -> ResumeProfile:
    return ResumeProfile(
        candidate_id="candidate_001",
        name="Test Candidate",
        summary="Data Scientist with Python and SQL experience.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
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
                description="Built a machine learning churn model.",
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
        certifications=[
            "Machine Learning Certification",
        ],
    )


def test_resume_agent_analyze():
    agent = ResumeAgent()

    result = agent.analyze(sample_resume())

    assert result["candidate_id"] == "candidate_001"
    assert result["name"] == "Test Candidate"
    assert result["skills"] == [
        "Python",
        "SQL",
        "Machine Learning",
    ]
    assert result["total_experience_years"] == 1.5
    assert result["project_count"] == 1


def test_resume_agent_preserves_projects():
    agent = ResumeAgent()

    result = agent.analyze(sample_resume())

    assert result["projects"][0]["name"] == "Churn Prediction"
    assert "Python" in result["projects"][0]["technologies"]


def test_resume_agent_preserves_education():
    agent = ResumeAgent()

    result = agent.analyze(sample_resume())

    assert result["education"][0]["degree"] == "Bachelor's Degree"
    assert result["education"][0]["field"] == "Computer Science"


def test_resume_agent_requires_resume():
    agent = ResumeAgent()

    try:
        agent.analyze(None)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_resume_agent_requires_rag_for_evidence():
    agent = ResumeAgent()

    try:
        agent.retrieve_relevant_evidence("machine learning")
        assert False, "Expected RuntimeError"
    except RuntimeError:
        pass