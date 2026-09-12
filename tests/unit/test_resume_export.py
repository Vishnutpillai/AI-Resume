from pathlib import Path

from docx import Document

from app.schemas.resume import (
    Education,
    Experience,
    Project,
    ResumeProfile,
)
from app.services.resume_export_service import ResumeExportService


def sample_resume():
    return ResumeProfile(
        candidate_id="candidate_001",
        name="Test Candidate",
        summary="Data Scientist with Python experience.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        experience=[
            Experience(
                company="ABC Technologies",
                role="Data Scientist",
                years=1.5,
            )
        ],
        projects=[
            Project(
                name="Churn Prediction",
                description="Built a churn model.",
                technologies=[
                    "Python",
                    "Scikit-learn",
                ],
            )
        ],
        education=[
            Education(
                degree="Bachelor's Degree",
                field="Computer Science",
                institution="Test University",
                year=2024,
            )
        ],
        certifications=[
            "Machine Learning Certification",
        ],
    )


def test_resume_export_creates_docx(tmp_path):
    service = ResumeExportService()

    output_path = (
        tmp_path / "resume.docx"
    )

    result = service.export_to_docx(
        resume=sample_resume(),
        output_path=str(output_path),
    )

    assert result == str(output_path)
    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_exported_docx_contains_resume_content(tmp_path):
    service = ResumeExportService()

    output_path = (
        tmp_path / "resume.docx"
    )

    service.export_to_docx(
        resume=sample_resume(),
        output_path=str(output_path),
    )

    document = Document(output_path)

    text = "\n".join(
        paragraph.text
        for paragraph in document.paragraphs
    )

    assert "Test Candidate" in text
    assert "Python" in text
    assert "Data Scientist" in text
    assert "Churn Prediction" in text
    assert "Test University" in text


def test_export_requires_resume(tmp_path):
    service = ResumeExportService()

    try:
        service.export_to_docx(
            resume=None,
            output_path=str(
                tmp_path / "resume.docx"
            ),
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass