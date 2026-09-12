from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class ResumeRecord(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    candidate_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    resume_text: Mapped[str] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class JobRecord(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    job_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
    )

    company: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    job_text: Mapped[str] = mapped_column(
        Text,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class MatchRecord(Base):
    __tablename__ = "match_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    candidate_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    job_id: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    overall_score: Mapped[float] = mapped_column(
        Float,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )