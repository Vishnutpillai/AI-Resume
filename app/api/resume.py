from fastapi import APIRouter

from app.schemas.api import ResumeAnalysisRequest


router = APIRouter(
    prefix="/api/v1/resume",
    tags=["Resume"],
)


@router.post("/analyze")
def analyze_resume(
    request: ResumeAnalysisRequest,
) -> dict[str, object]:
    return {
        "candidate_id": request.candidate_id,
        "name": request.name,
        "message": "Resume received successfully.",
        "text_length": len(request.resume_text),
        "skills": request.skills,
    }