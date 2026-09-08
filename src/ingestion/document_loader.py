from pathlib import Path

from src.ingestion.file_validator import validate_file
from src.parsing.pdf_parser import parse_pdf
from src.parsing.docx_parser import parse_docx
from src.parsing.json_parser import parse_json
from src.parsing.image_parser import parse_image


def load_document(file_path: str) -> str:
    """
    Load a supported document and return extracted text.
    """

    path = validate_file(file_path)

    extension = path.suffix.lower()

    if extension == ".pdf":
        return parse_pdf(path)

    if extension == ".docx":
        return parse_docx(path)

    if extension == ".json":
        return parse_json(path)

    if extension in {".jpg", ".jpeg", ".png"}:
        return parse_image(path)

    if extension == ".txt":
        return path.read_text(
            encoding="utf-8"
        )

    raise ValueError(
        f"Unsupported document type: {extension}"
    )