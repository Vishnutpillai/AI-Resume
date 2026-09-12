from rank_bm25 import BM25Okapi


class BM25Retriever:
    """
    Keyword-based document retriever using BM25.
    """

    def __init__(self, documents: list[str] | None = None):
        self.documents: list[str] = []
        self.tokenized_documents: list[list[str]] = []
        self.bm25: BM25Okapi | None = None

        if documents:
            self.build(documents)

    @staticmethod
    def tokenize(text: str) -> list[str]:
        if not text:
            return []

        return text.lower().split()

    def build(self, documents: list[str]) -> None:
        if not documents:
            raise ValueError("At least one document is required.")

        self.documents = documents
        self.tokenized_documents = [
            self.tokenize(document)
            for document in documents
        ]

        self.bm25 = BM25Okapi(self.tokenized_documents)

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, object]]:
        if not query or not query.strip():
            return []

        if self.bm25 is None:
            raise RuntimeError("BM25 index has not been built.")

        if top_k <= 0:
            return []

        scores = self.bm25.get_scores(
            self.tokenize(query)
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        results = []

        for index in ranked_indices[:top_k]:
            results.append(
                {
                    "document": self.documents[index],
                    "score": float(scores[index]),
                    "index": index,
                }
            )

        return results