from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.schemas.resume import ResumeProfile
from app.services.resume_export_service import (
    ResumeExportService,
)


router = APIRouter(
    prefix="/api/v1/export",
    tags=["Export"],
)


@router.post(
    "/docx",
    response_class=FileResponse,
)
def export_docx(
    resume: ResumeProfile,
):
    """
    Export a ResumeProfile as a DOCX file.

    FastAPI validates ResumeProfile automatically.
    Invalid request bodies therefore return HTTP 422.
    """

    service = ResumeExportService()

    # Create a temporary output file.
    temp_directory = Path(
        tempfile.gettempdir()
    ) / "intelligent_resume_job_matcher"

    temp_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        temp_directory
        / f"{resume.candidate_id}_resume.docx"
    )


    service.export_to_docx(
        resume=resume,
        output_path=str(output_path),
    )


    return FileResponse(
        path=str(output_path),
        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        filename="resume.docx",
    )