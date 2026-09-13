from __future__ import annotations

from pathlib import Path

from docx import Document

from app.schemas.resume import ResumeProfile


class ResumeExportService:
    """
    Export ResumeProfile objects to DOCX.
    """

    def export_to_docx(
        self,
        resume: ResumeProfile,
        output_path: str,
    ) -> str:
        """
        Create a DOCX file from a ResumeProfile.

        Returns:
            Absolute output path as a string.
        """

        if resume is None:
            raise ValueError(
                "Resume profile is required."
            )

        if not isinstance(
            resume,
            ResumeProfile,
        ):
            raise TypeError(
                "resume must be a ResumeProfile."
            )

        path = Path(
            output_path
        )

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = Document()

        # ====================================================
        # NAME
        # ====================================================

        if resume.name:

            document.add_heading(
                resume.name,
                level=1,
            )


        # ====================================================
        # SUMMARY
        # ====================================================

        if resume.summary:

            document.add_heading(
                "Summary",
                level=2,
            )

            document.add_paragraph(
                resume.summary
            )


        # ====================================================
        # SKILLS
        # ====================================================

        if resume.skills:

            document.add_heading(
                "Skills",
                level=2,
            )

            document.add_paragraph(
                ", ".join(
                    resume.skills
                )
            )


        # ====================================================
        # EXPERIENCE
        # ====================================================

        if resume.experience:

            document.add_heading(
                "Experience",
                level=2,
            )

            for experience in resume.experience:

                paragraph = (
                    document.add_paragraph()
                )

                title_parts = []

                if experience.role:
                    title_parts.append(
                        experience.role
                    )

                if experience.company:
                    title_parts.append(
                        experience.company
                    )

                title = " — ".join(
                    title_parts
                )

                if title:

                    paragraph.add_run(
                        title
                    ).bold = True


                if experience.years:

                    paragraph.add_run(
                        f" ({experience.years:g} years)"
                    )


        # ====================================================
        # PROJECTS
        # ====================================================

        if resume.projects:

            document.add_heading(
                "Projects",
                level=2,
            )

            for project in resume.projects:

                # Project heading/content paragraph
                paragraph = (
                    document.add_paragraph()
                )

                if project.name:

                    paragraph.add_run(
                        project.name
                    ).bold = True


                if project.description:

                    paragraph.add_run(
                        f" — {project.description}"
                    )


                # Technologies
                if project.technologies:

                    technology_paragraph = (
                        document.add_paragraph()
                    )

                    technology_paragraph.add_run(
                        "Technologies: "
                    ).bold = True

                    technology_paragraph.add_run(
                        ", ".join(
                            project.technologies
                        )
                    )


        # ====================================================
        # EDUCATION
        # ====================================================

        if resume.education:

            document.add_heading(
                "Education",
                level=2,
            )

            for education in resume.education:

                paragraph = (
                    document.add_paragraph()
                )

                parts = []

                if education.degree:
                    parts.append(
                        education.degree
                    )

                if education.field:
                    parts.append(
                        education.field
                    )

                if education.institution:
                    parts.append(
                        education.institution
                    )

                if education.year:
                    parts.append(
                        str(education.year)
                    )

                if parts:

                    paragraph.add_run(
                        " | ".join(parts)
                    )


        # ====================================================
        # CERTIFICATIONS
        # ====================================================

        if resume.certifications:

            document.add_heading(
                "Certifications",
                level=2,
            )

            for certification in (
                resume.certifications
            ):

                document.add_paragraph(
                    certification,
                    style="List Bullet",
                )


        # ====================================================
        # SAVE
        # ====================================================

        document.save(
            str(path)
        )

        return str(
            path
        )