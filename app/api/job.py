from fastapi import APIRouter

from app.schemas.api import JobAnalysisRequest


router = APIRouter(
    prefix="/api/v1/job",
    tags=["Job"],
)


@router.post("/analyze")
def analyze_job(
    request: JobAnalysisRequest,
) -> dict[str, object]:
    return {
        "job_id": request.job_id,
        "title": request.title,
        "message": "Job description received successfully.",
        "text_length": len(request.job_text),
        "required_skills": request.required_skills,
    }