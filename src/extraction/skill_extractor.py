import re


SKILL_DICTIONARY = [
    # Programming
    "python",
    "sql",
    "javascript",

    # Databases
    "mysql",
    "postgresql",

    # Data Science
    "pandas",
    "numpy",
    "exploratory data analysis",
    "eda",
    "predictive modeling",
    "feature engineering",

    # Machine Learning
    "machine learning",
    "supervised learning",
    "unsupervised learning",
    "scikit-learn",
    "cross validation",
    "xgboost",

    # Deep Learning
    "deep learning",
    "neural networks",
    "tensorflow",
    "pytorch",

    # AI
    "computer vision",
    "natural language processing",
    "nlp",

    # MLOps
    "mlops",
    "dvc",
    "feast",
    "data versioning",
    "feature management",
    "ci/cd",

    # Cloud
    "aws",
    "aws s3",
    "azure",
    "gcp",

    # Backend / Deployment
    "flask",
    "fastapi",
    "streamlit",
    "docker",

    # Development
    "git",
    "github",

    # GenAI
    "langchain",
    "langgraph",
    "ollama",
    "rag",
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