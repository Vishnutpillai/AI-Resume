from functools import lru_cache

from sentence_transformers import CrossEncoder


DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class Reranker:
    """
    Rerank retrieved documents using a cross-encoder.

    The cross-encoder directly evaluates query-document pairs,
    making it useful for improving the ordering produced by
    vector and keyword retrieval.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_RERANKER_MODEL,
    ):
        self.model_name = model_name
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        results: list[dict[str, object]],
        top_k: int = 5,
    ) -> list[dict[str, object]]:
        if not query or not query.strip():
            return []

        if not results:
            return []

        if top_k <= 0:
            return []

        pairs = [
            (
                query,
                str(result["document"]),
            )
            for result in results
        ]

        scores = self.model.predict(pairs)

        reranked = []

        for result, score in zip(results, scores):
            item = dict(result)

            item["reranker_score"] = float(score)

            reranked.append(item)

        reranked.sort(
            key=lambda result: float(result["reranker_score"]),
            reverse=True,
        )

        return reranked[:top_k]


@lru_cache(maxsize=1)
def get_reranker() -> Reranker:
    return Reranker()