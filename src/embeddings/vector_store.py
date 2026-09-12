from pathlib import Path

import faiss
import numpy as np


class VectorStore:
    """Simple FAISS vector store for semantic retrieval."""

    def __init__(self, dimension: int):
        if dimension <= 0:
            raise ValueError("Vector dimension must be greater than zero.")

        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.documents: list[str] = []

    def add(self, embeddings, documents: list[str]) -> None:
        if len(embeddings) != len(documents):
            raise ValueError(
                "Number of embeddings must match number of documents."
            )

        if not documents:
            return

        vectors = np.asarray(embeddings, dtype="float32")

        if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Expected embeddings with shape (n, {self.dimension}), "
                f"got {vectors.shape}."
            )

        self.index.add(vectors)
        self.documents.extend(documents)

    def search(
        self,
        query_embedding,
        top_k: int = 5,
    ) -> list[dict[str, object]]:
        if top_k <= 0:
            return []

        if self.index.ntotal == 0:
            return []

        query = np.asarray(query_embedding, dtype="float32")

        if query.ndim == 1:
            query = query.reshape(1, -1)

        if query.shape != (1, self.dimension):
            raise ValueError(
                f"Expected query embedding shape (1, {self.dimension}), "
                f"got {query.shape}."
            )

        k = min(top_k, self.index.ntotal)

        scores, indices = self.index.search(query, k)

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue

            results.append(
                {
                    "document": self.documents[index],
                    "score": float(score),
                    "index": int(index),
                }
            )

        return results

    def save(self, index_path: str, documents_path: str) -> None:
        index_path = Path(index_path)
        documents_path = Path(documents_path)

        index_path.parent.mkdir(parents=True, exist_ok=True)
        documents_path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(index_path))

        documents_path.write_text(
            "\n".join(self.documents),
            encoding="utf-8",
        )

    @classmethod
    def load(
        cls,
        index_path: str,
        documents_path: str,
    ) -> "VectorStore":
        index = faiss.read_index(str(index_path))

        documents_path = Path(documents_path)

        if documents_path.exists():
            content = documents_path.read_text(
                encoding="utf-8"
            )

            documents = content.splitlines()

            if not content:
                documents = []
        else:
            documents = []

        store = cls(dimension=index.d)
        store.index = index
        store.documents = documents

        if store.index.ntotal != len(store.documents):
            raise ValueError(
                "FAISS index size does not match stored documents."
            )

        return store