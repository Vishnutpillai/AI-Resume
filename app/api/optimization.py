from fastapi import APIRouter

from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile
from src.optimization.optimization_pipeline import run_optimization_pipeline


router = APIRouter(
    prefix="/api/v1/optimization",
    tags=["Optimization"],
)


@router.post("")
def optimize_resume(
    resume: dict,
    job: dict,
    resume_text: str,
    job_text: str,
) -> dict[str, object]:
    resume_profile = ResumeProfile.model_validate(resume)
    job_profile = JobProfile.model_validate(job)

    result = run_optimization_pipeline(
        resume=resume_profile,
        job=job_profile,
        resume_text=resume_text,
        job_text=job_text,
    )

    return result