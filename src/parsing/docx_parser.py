from pathlib import Path

from docx import Document


def parse_docx(file_path: Path) -> str:
    """
    Extract text from a DOCX document.
    """

    document = Document(str(file_path))

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)