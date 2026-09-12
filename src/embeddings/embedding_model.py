from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import settings


class EmbeddingModel:
    """Generate normalized sentence embeddings."""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or settings.embedding_model
        self.model = SentenceTransformer(self.model_name)

    def encode(self, texts: list[str]):
        if not texts:
            return []

        return self.model.encode(
            texts,
            normalize_embeddings=True,
        )


@lru_cache(maxsize=1)
def get_embedding_model() -> EmbeddingModel:
    """Return a cached embedding model instance."""
    return EmbeddingModel()