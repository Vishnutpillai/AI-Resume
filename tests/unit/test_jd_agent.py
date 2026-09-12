from app.schemas.job import JobProfile
from src.agents.jd_agent import JDAgent


def sample_job() -> JobProfile:
    return JobProfile(
        job_id="job_001",
        title="Data Scientist",
        company="ABC Technologies",
        description=(
            "Develop machine learning models and predictive solutions."
        ),
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        preferred_skills=[
            "Docker",
            "AWS",
            "FastAPI",
        ],
        minimum_experience=1.0,
        education="Bachelor's degree in Computer Science",
        keywords=[
            "Data Scientist",
            "Python",
            "Machine Learning",
            "Predictive Modeling",
        ],
    )


def test_jd_agent_analyze():
    agent = JDAgent()

    result = agent.analyze(sample_job())

    assert result["job_id"] == "job_001"
    assert result["title"] == "Data Scientist"
    assert result["company"] == "ABC Technologies"


def test_jd_agent_preserves_required_skills():
    agent = JDAgent()

    result = agent.analyze(sample_job())

    assert result["required_skills"] == [
        "Python",
        "SQL",
        "Machine Learning",
    ]


def test_jd_agent_preserves_preferred_skills():
    agent = JDAgent()

    result = agent.analyze(sample_job())

    assert "Docker" in result["preferred_skills"]
    assert "AWS" in result["preferred_skills"]


def test_jd_agent_preserves_job_requirements():
    agent = JDAgent()

    result = agent.analyze(sample_job())

    assert result["minimum_experience"] == 1.0
    assert result["education"] == (
        "Bachelor's degree in Computer Science"
    )


def test_jd_agent_requires_job():
    agent = JDAgent()

    try:
        agent.analyze(None)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_jd_agent_requires_rag_for_evidence():
    agent = JDAgent()

    try:
        agent.retrieve_relevant_evidence("Python machine learning")
        assert False, "Expected RuntimeError"
    except RuntimeError:
        pass