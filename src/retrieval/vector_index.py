from pathlib import Path

from src.embeddings.embedding_model import get_embedding_model
from src.embeddings.vector_store import VectorStore
from src.retrieval.chunker import TextChunk


class PersistentVectorIndex:
    """
    Build, save, load, and search a persistent FAISS vector index.
    """

    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.store: VectorStore | None = None

    def build(self, chunks: list[TextChunk]) -> VectorStore:
        if not chunks:
            raise ValueError("At least one text chunk is required.")

        documents = [chunk.text for chunk in chunks]
        embeddings = self.embedding_model.encode(documents)

        self.store = VectorStore(
            dimension=embeddings.shape[1],
        )

        self.store.add(
            embeddings=embeddings,
            documents=documents,
        )

        return self.store

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, object]]:
        if not query or not query.strip():
            return []

        if self.store is None:
            raise RuntimeError("Vector index has not been built or loaded.")

        query_embedding = self.embedding_model.encode([query])[0]

        return self.store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

    def save(
        self,
        index_path: str,
        documents_path: str,
    ) -> None:
        if self.store is None:
            raise RuntimeError("Vector index has not been built.")

        self.store.save(
            index_path=index_path,
            documents_path=documents_path,
        )

    def load(
        self,
        index_path: str,
        documents_path: str,
    ) -> None:
        if not Path(index_path).exists():
            raise FileNotFoundError(index_path)

        self.store = VectorStore.load(
            index_path=index_path,
            documents_path=documents_path,
        )