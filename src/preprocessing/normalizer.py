import re


def normalize_text(text: str) -> str:
    """
    Normalize text for downstream NLP processing.
    """

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()