from app.models import JobRecord, MatchRecord, ResumeRecord
from app.models.database import Base


def test_database_models_registered():
    tables = Base.metadata.tables

    assert "resumes" in tables
    assert "jobs" in tables
    assert "match_results" in tables


def test_resume_record_columns():
    columns = ResumeRecord.__table__.columns

    assert "candidate_id" in columns
    assert "name" in columns
    assert "resume_text" in columns


def test_job_record_columns():
    columns = JobRecord.__table__.columns

    assert "job_id" in columns
    assert "title" in columns
    assert "job_text" in columns


def test_match_record_columns():
    columns = MatchRecord.__table__.columns

    assert "candidate_id" in columns
    assert "job_id" in columns
    assert "overall_score" in columns