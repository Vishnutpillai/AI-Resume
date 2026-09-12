from pathlib import Path
from tempfile import gettempdir

from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.schemas.resume import ResumeProfile
from app.services.resume_export_service import ResumeExportService


router = APIRouter(
    prefix="/api/v1/export",
    tags=["Export"],
)


@router.post("/docx")
def export_docx(
    resume: ResumeProfile,
):
    output_path = (
        Path(gettempdir())
        / "optimized_resume.docx"
    )

    service = ResumeExportService()

    service.export_to_docx(
        resume=resume,
        output_path=str(output_path),
    )

    return FileResponse(
        path=output_path,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        filename="optimized_resume.docx",
    )