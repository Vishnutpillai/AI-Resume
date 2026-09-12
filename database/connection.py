from app.models.database import Base, engine
from app.models import JobRecord, MatchRecord, ResumeRecord


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)