from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.schemas.api import AnalysisRequest
from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile
from app.services.analysis_service import AnalysisService


router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)


@router.post("")
def analyze(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
) -> dict[str, object]:
    resume = ResumeProfile.model_validate(
        request.resume
    )

    job = JobProfile.model_validate(
        request.job
    )

    service = AnalysisService()

    return service.analyze(
        db=db,
        resume=resume,
        job=job,
        resume_text=request.resume_text,
        job_text=request.job_text,
        use_llm=request.use_llm,
    )