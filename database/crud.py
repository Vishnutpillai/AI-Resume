from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import (
    JobRecord,
    MatchRecord,
    ResumeRecord,
)


def create_resume(
    db: Session,
    candidate_id: str,
    name: str | None,
    resume_text: str,
) -> ResumeRecord:
    record = ResumeRecord(
        candidate_id=candidate_id,
        name=name,
        resume_text=resume_text,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def get_resume(
    db: Session,
    candidate_id: str,
) -> ResumeRecord | None:
    statement = select(ResumeRecord).where(
        ResumeRecord.candidate_id == candidate_id
    )

    return db.execute(statement).scalar_one_or_none()


def create_job(
    db: Session,
    job_id: str,
    title: str,
    company: str | None,
    job_text: str,
) -> JobRecord:
    record = JobRecord(
        job_id=job_id,
        title=title,
        company=company,
        job_text=job_text,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def get_job(
    db: Session,
    job_id: str,
) -> JobRecord | None:
    statement = select(JobRecord).where(
        JobRecord.job_id == job_id
    )

    return db.execute(statement).scalar_one_or_none()


def create_match_result(
    db: Session,
    candidate_id: str,
    job_id: str,
    overall_score: float,
) -> MatchRecord:
    record = MatchRecord(
        candidate_id=candidate_id,
        job_id=job_id,
        overall_score=overall_score,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def get_match_results(
    db: Session,
    candidate_id: str,
    job_id: str,
) -> list[MatchRecord]:
    statement = (
        select(MatchRecord)
        .where(
            MatchRecord.candidate_id == candidate_id,
            MatchRecord.job_id == job_id,
        )
        .order_by(MatchRecord.created_at.desc())
    )

    return list(db.execute(statement).scalars().all())