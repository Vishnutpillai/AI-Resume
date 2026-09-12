from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile
from src.agents.skill_agent import SkillAgent


def sample_resume() -> ResumeProfile:
    return ResumeProfile(
        candidate_id="candidate_001",
        name="Test Candidate",
        skills=[
            "Python",
            "SQL",
            "Pandas",
            "Machine Learning",
        ],
    )


def sample_job() -> JobProfile:
    return JobProfile(
        job_id="job_001",
        title="Data Scientist",
        required_skills=[
            "Python",
            "SQL",
            "Scikit-learn",
            "XGBoost",
        ],
        preferred_skills=[
            "Docker",
            "AWS",
        ],
    )


def test_skill_agent_analyze():
    agent = SkillAgent()

    result = agent.analyze(
        resume=sample_resume(),
        job=sample_job(),
    )

    assert result["candidate_id"] == "candidate_001"
    assert result["job_id"] == "job_001"


def test_skill_agent_detects_matched_skills():
    agent = SkillAgent()

    result = agent.analyze(
        resume=sample_resume(),
        job=sample_job(),
    )

    assert "Python" in result["matched_required_skills"]
    assert "SQL" in result["matched_required_skills"]


def test_skill_agent_detects_missing_required_skills():
    agent = SkillAgent()

    result = agent.analyze(
        resume=sample_resume(),
        job=sample_job(),
    )

    assert "Scikit-learn" in result["missing_required_skills"]
    assert "XGBoost" in result["missing_required_skills"]


def test_skill_agent_detects_missing_preferred_skills():
    agent = SkillAgent()

    result = agent.analyze(
        resume=sample_resume(),
        job=sample_job(),
    )

    assert "Docker" in result["missing_preferred_skills"]
    assert "AWS" in result["missing_preferred_skills"]


def test_skill_agent_requires_resume():
    agent = SkillAgent()

    try:
        agent.analyze(
            resume=None,
            job=sample_job(),
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_skill_agent_requires_job():
    agent = SkillAgent()

    try:
        agent.analyze(
            resume=sample_resume(),
            job=None,
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_skill_agent_requires_rag_for_evidence():
    agent = SkillAgent()

    try:
        agent.retrieve_relevant_evidence(
            "Python machine learning"
        )
        assert False, "Expected RuntimeError"
    except RuntimeError:
        pass