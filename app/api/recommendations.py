from fastapi import APIRouter

from app.schemas.api import JobRecommendationRequest
from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile
from app.services.job_recommendation_service import (
    JobRecommendationService,
)


router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["Recommendations"],
)


@router.post("")
def recommend_jobs(
    request: JobRecommendationRequest,
) -> dict[str, object]:
    resume = ResumeProfile.model_validate(
        request.resume
    )

    jobs = [
        JobProfile.model_validate(job)
        for job in request.jobs
    ]

    service = JobRecommendationService()

    results = service.recommend(
        resume=resume,
        resume_text=request.resume_text,
        jobs=jobs,
        job_texts=request.job_texts,
    )

    return {
        "candidate_id": resume.candidate_id,
        "total_jobs": len(results),
        "recommendations": results,
    }