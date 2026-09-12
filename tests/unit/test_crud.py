from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.database import Base
from database.crud import (
    create_job,
    create_match_result,
    create_resume,
    get_job,
    get_match_results,
    get_resume,
)


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


def test_create_and_get_resume():
    db = create_test_db()

    created = create_resume(
        db=db,
        candidate_id="candidate_001",
        name="Test Candidate",
        resume_text="Python SQL Machine Learning",
    )

    assert created.id is not None
    assert created.candidate_id == "candidate_001"

    retrieved = get_resume(
        db=db,
        candidate_id="candidate_001",
    )

    assert retrieved is not None
    assert retrieved.name == "Test Candidate"
    assert retrieved.resume_text == "Python SQL Machine Learning"

    db.close()


def test_create_and_get_job():
    db = create_test_db()

    created = create_job(
        db=db,
        job_id="job_001",
        title="Data Scientist",
        company="ABC Technologies",
        job_text="Python SQL Machine Learning",
    )

    assert created.id is not None
    assert created.job_id == "job_001"

    retrieved = get_job(
        db=db,
        job_id="job_001",
    )

    assert retrieved is not None
    assert retrieved.title == "Data Scientist"

    db.close()


def test_create_and_get_match_results():
    db = create_test_db()

    create_match_result(
        db=db,
        candidate_id="candidate_001",
        job_id="job_001",
        overall_score=82.5,
    )

    create_match_result(
        db=db,
        candidate_id="candidate_001",
        job_id="job_001",
        overall_score=87.0,
    )

    results = get_match_results(
        db=db,
        candidate_id="candidate_001",
        job_id="job_001",
    )

    assert len(results) == 2
    assert results[0].overall_score == 87.0
    assert results[1].overall_score == 82.5

    db.close()