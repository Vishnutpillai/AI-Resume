from functools import lru_cache

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings


class SemanticMatcher:
    """
    Calculate semantic similarity between resume and job description.

    The SentenceTransformer model is cached so it is loaded only once
    per model name instead of being initialized for every comparison.
    """

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self.model = get_embedding_model(self.model_name)

    def calculate_similarity(
        self,
        resume_text: str,
        job_text: str,
    ) -> float:
        """
        Calculate cosine similarity between resume and job description.

        Returns:
            Similarity score between 0 and 100.
        """

        if not resume_text or not job_text:
            return 0.0

        embeddings = self.model.encode(
            [resume_text, job_text],
            normalize_embeddings=True,
        )

        similarity = cosine_similarity(
            [embeddings[0]],
            [embeddings[1]],
        )[0][0]

        similarity = max(
            0.0,
            min(1.0, float(similarity)),
        )

        return round(similarity * 100, 2)


@lru_cache(maxsize=4)
def get_embedding_model(
    model_name: str,
) -> SentenceTransformer:
    """
    Load and cache the embedding model.

    This prevents repeated Hugging Face/model initialization during
    multiple job comparisons in the same process.
    """

    return SentenceTransformer(model_name)


def calculate_semantic_score(
    resume_text: str,
    job_text: str,
) -> float:
    """
    Convenience function for semantic matching.
    """

    matcher = SemanticMatcher()

    return matcher.calculate_similarity(
        resume_text=resume_text,
        job_text=job_text,
    )