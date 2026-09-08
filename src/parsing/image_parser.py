from pathlib import Path

from PIL import Image
import pytesseract

from app.core.config import settings


pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd



def parse_image(file_path: Path) -> str:
    """
    Extract text from an image using OCR.
    """

    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)

    return text