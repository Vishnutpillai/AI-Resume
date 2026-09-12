from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base
from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile

from src.agents.llm_arbitrator import LLMArbitrator
from src.agents.orchestrator import AgentOrchestrator

from app.services.analysis_service import AnalysisService


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
    )

    Base.metadata.create_all(bind=engine)

    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    return session_factory()


def sample_resume():
    return ResumeProfile(
        candidate_id="candidate_001",
        name="Test Candidate",
        summary="Data Scientist with Python experience.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
    )


def sample_job():
    return JobProfile(
        job_id="job_001",
        title="Data Scientist",
        description="Build machine learning solutions.",
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        preferred_skills=[
            "Docker",
        ],
    )


def test_analysis_service_without_llm():
    db = create_test_db()

    service = AnalysisService(
        orchestrator=AgentOrchestrator(),
        arbitrator=LLMArbitrator(),
    )

    result = service.analyze(
        db=db,
        resume=sample_resume(),
        job=sample_job(),
        resume_text="Python SQL Machine Learning",
        job_text="Python SQL Machine Learning",
        use_llm=False,
    )

    assert result["candidate_id"] == "candidate_001"
    assert result["job_id"] == "job_001"
    assert result["match_record_id"] is not None
    assert "deterministic_analysis" in result
    assert "llm_analysis" not in result

    db.close()