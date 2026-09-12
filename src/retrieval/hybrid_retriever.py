from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.vector_index import PersistentVectorIndex


class HybridRetriever:
    """
    Combine semantic vector retrieval and BM25 keyword retrieval.
    """

    def __init__(
        self,
        vector_index: PersistentVectorIndex,
        bm25_retriever: BM25Retriever,
        vector_weight: float = 0.6,
        bm25_weight: float = 0.4,
    ):
        if vector_weight < 0 or bm25_weight < 0:
            raise ValueError("Retrieval weights cannot be negative.")

        if vector_weight + bm25_weight <= 0:
            raise ValueError("At least one retrieval weight must be greater than zero.")

        self.vector_index = vector_index
        self.bm25_retriever = bm25_retriever
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight

    @staticmethod
    def _normalize_scores(
        results: list[dict[str, object]],
    ) -> dict[int, float]:
        if not results:
            return {}

        scores = [
            float(result["score"])
            for result in results
        ]

        minimum = min(scores)
        maximum = max(scores)

        if maximum == minimum:
            return {
                int(result["index"]): 1.0
                for result in results
            }

        return {
            int(result["index"]): (
                float(result["score"]) - minimum
            ) / (maximum - minimum)
            for result in results
        }

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, object]]:
        if not query or not query.strip():
            return []

        vector_results = self.vector_index.search(
            query=query,
            top_k=top_k,
        )

        bm25_results = self.bm25_retriever.search(
            query=query,
            top_k=top_k,
        )

        vector_scores = self._normalize_scores(vector_results)
        bm25_scores = self._normalize_scores(bm25_results)

        documents: dict[int, str] = {}

        for result in vector_results:
            index = int(result["index"])
            documents[index] = str(result["document"])

        for result in bm25_results:
            index = int(result["index"])
            documents[index] = str(result["document"])

        combined_results = []

        for index, document in documents.items():
            vector_score = vector_scores.get(index, 0.0)
            bm25_score = bm25_scores.get(index, 0.0)

            hybrid_score = (
                self.vector_weight * vector_score
                + self.bm25_weight * bm25_score
            )

            combined_results.append(
                {
                    "document": document,
                    "score": float(hybrid_score),
                    "index": index,
                    "vector_score": float(vector_score),
                    "bm25_score": float(bm25_score),
                }
            )

        combined_results.sort(
            key=lambda result: float(result["score"]),
            reverse=True,
        )

        return combined_results[:top_k]