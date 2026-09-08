import re


SKILL_DICTIONARY = [
    "python",
    "sql",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "fastapi",
    "docker",
    "aws",
    "azure",
    "gcp",
    "spark",
    "pyspark",
    "git",
    "github",
    "langchain",
    "langgraph",
    "ollama",
    "rag",
    "postgresql",
]


def extract_skills(text: str) -> list[str]:
    """
    Extract known technical skills from text.
    """

    if not text:
        return []

    normalized_text = text.lower()

    found_skills = []

    for skill in SKILL_DICTIONARY:
        pattern = rf"\b{re.escape(skill)}\b"

        if re.search(pattern, normalized_text):
            found_skills.append(skill)

    return found_skills