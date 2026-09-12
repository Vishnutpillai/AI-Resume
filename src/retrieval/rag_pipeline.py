from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.chunker import TextChunk, chunk_text
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.vector_index import PersistentVectorIndex
from src.reranking.reranker import get_reranker


class RAGPipeline:
    """
    Retrieval-Augmented Generation preparation pipeline.

    This step focuses on retrieval and context construction.
    LLM generation will be added later in Phase 4.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 100,
        vector_weight: float = 0.6,
        bm25_weight: float = 0.4,
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap

        self.vector_index = PersistentVectorIndex()
        self.bm25_retriever: BM25Retriever | None = None
        self.hybrid_retriever: HybridRetriever | None = None

        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight

    def build(self, text: str, source: str = "document") -> list[TextChunk]:
        if not text or not text.strip():
            raise ValueError("Text is required to build the RAG pipeline.")

        chunks = chunk_text(
            text=text,
            source=source,
            chunk_size=self.chunk_size,
            overlap=self.overlap,
        )

        if not chunks:
            raise ValueError("No chunks were created from the provided text.")

        self.vector_index.build(chunks)

        documents = [chunk.text for chunk in chunks]

        self.bm25_retriever = BM25Retriever(documents)

        self.hybrid_retriever = HybridRetriever(
            vector_index=self.vector_index,
            bm25_retriever=self.bm25_retriever,
            vector_weight=self.vector_weight,
            bm25_weight=self.bm25_weight,
        )

        return chunks

    def retrieve(
        self,
        query: str,
        retrieval_k: int = 10,
        top_k: int = 5,
    ) -> list[dict[str, object]]:
        if not query or not query.strip():
            return []

        if self.hybrid_retriever is None:
            raise RuntimeError("RAG pipeline has not been built.")

        hybrid_results = self.hybrid_retriever.search(
            query=query,
            top_k=retrieval_k,
        )

        reranker = get_reranker()

        return reranker.rerank(
            query=query,
            results=hybrid_results,
            top_k=top_k,
        )

    def build_context(
        self,
        results: list[dict[str, object]],
    ) -> str:
        if not results:
            return ""

        context_parts = []

        for position, result in enumerate(results, start=1):
            document = str(result["document"])

            context_parts.append(
                f"[Context {position}]\n{document}"
            )

        return "\n\n".join(context_parts)

    def query(
        self,
        query: str,
        retrieval_k: int = 10,
        top_k: int = 5,
    ) -> dict[str, object]:
        results = self.retrieve(
            query=query,
            retrieval_k=retrieval_k,
            top_k=top_k,
        )

        context = self.build_context(results)

        return {
            "query": query,
            "results": results,
            "context": context,
        }