import re


def clean_text(text: str) -> str:
    """
    Clean extracted text while preserving useful content.
    """

    if not text:
        return ""

    text = text.replace("\r", "\n")

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()