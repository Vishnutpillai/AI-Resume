from pathlib import Path

from app.schemas import resume
from docx import Document

from app.schemas.resume import ResumeProfile


class ResumeExportService:
    """
    Convert a ResumeProfile into a DOCX document.
    """

    def export_to_docx(
        self,
        resume: ResumeProfile,
        output_path: str,
    ) -> str:
        if not resume:
            raise ValueError("Resume profile is required.")

        path = Path(output_path)
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = Document()

        if resume.name:
            document.add_heading(
                resume.name,
                level=1,
            )

        if resume.summary:
            document.add_heading(
                "Summary",
                level=2,
            )
            document.add_paragraph(
                resume.summary
            )

        if resume.skills:
            document.add_heading(
                "Skills",
                level=2,
            )
            document.add_paragraph(
                ", ".join(resume.skills)
            )

        if resume.experience:
            document.add_heading(
                "Experience",
                level=2,
            )

            for experience in resume.experience:
                title = experience.role

                if experience.company:
                    title += f" — {experience.company}"

                paragraph = document.add_paragraph()

                paragraph.add_run(
                    title
                ).bold = True

                if experience.years:
                    paragraph.add_run(
                        f" ({experience.years:g} years)"
                    )

        if resume.projects:
            document.add_heading(
                "Projects",
                level=2,
            )

            for project in resume.projects:
                paragraph = document.add_paragraph()

                paragraph.add_run(
                    project.name
                ).bold = True

                if project.description:
                    paragraph.add_run(
                        f" — {project.description}"
                    )

                if project.technologies:
                    paragraph.add_run(
                        " | Technologies: "
                        + ", ".join(project.technologies)
                    )

        if resume.education:
            document.add_heading(
                "Education",
                level=2,
            )

            for education in resume.education:
                education_text = education.degree

                if education.field:
                    education_text += (
                        f" in {education.field}"
                    )

                if education.institution:
                    education_text += (
                        f" — {education.institution}"
                    )

                if education.year:
                    education_text += (
                        f" ({education.year})"
                    )

                document.add_paragraph(
                    education_text
                )

        if resume.certifications:
            document.add_heading(
                "Certifications",
                level=2,
            )

            for certification in resume.certifications:
                document.add_paragraph(
                    certification,
                    style="List Bullet",
                )

        document.save(path)

        return str(path)