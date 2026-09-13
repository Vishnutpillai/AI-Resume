from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.api import JobRecommendationRequest
from app.services.job_recommendation_service import (
    recommend_jobs,
)


router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["Recommendations"],
)


@router.post("")
def recommend(
    request: JobRecommendationRequest,
) -> dict[str, object]:
    """
    Rank multiple job descriptions against a resume.
    """

    try:

        result = recommend_jobs(
            resume=request.resume,
            resume_text=request.resume_text,
            jobs=request.jobs,
            job_texts=request.job_texts,
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        print(
            "Job recommendation error:",
            repr(exc),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Job recommendation processing failed. "
                "Check the FastAPI console for the traceback."
            ),
        ) from exc