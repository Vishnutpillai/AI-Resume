from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.chunker import chunk_text
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.vector_index import PersistentVectorIndex


def build_test_retrievers():
    documents = [
        "Python machine learning project using scikit-learn",
        "Docker deployment with FastAPI",
        "SQL database analytics",
    ]

    chunks = chunk_text(
        "\n\n".join(documents),
        source="test",
        chunk_size=200,
        overlap=20,
    )

    vector_index = PersistentVectorIndex()
    vector_index.build(chunks)

    bm25 = BM25Retriever(documents)

    return vector_index, bm25


def test_hybrid_search():
    vector_index, bm25 = build_test_retrievers()

    retriever = HybridRetriever(
        vector_index=vector_index,
        bm25_retriever=bm25,
    )

    results = retriever.search(
        "Python machine learning",
        top_k=3,
    )

    assert len(results) == 3
    assert results[0]["document"] == (
        "Python machine learning project using scikit-learn"
    )


def test_hybrid_results_contain_component_scores():
    vector_index, bm25 = build_test_retrievers()

    retriever = HybridRetriever(
        vector_index=vector_index,
        bm25_retriever=bm25,
    )

    results = retriever.search(
        "Python",
        top_k=2,
    )

    assert "score" in results[0]
    assert "vector_score" in results[0]
    assert "bm25_score" in results[0]


def test_hybrid_empty_query():
    vector_index, bm25 = build_test_retrievers()

    retriever = HybridRetriever(
        vector_index=vector_index,
        bm25_retriever=bm25,
    )

    assert retriever.search("") == []


def test_hybrid_rejects_invalid_weights():
    vector_index, bm25 = build_test_retrievers()

    try:
        HybridRetriever(
            vector_index=vector_index,
            bm25_retriever=bm25,
            vector_weight=0,
            bm25_weight=0,
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_hybrid_custom_weights():
    vector_index, bm25 = build_test_retrievers()

    retriever = HybridRetriever(
        vector_index=vector_index,
        bm25_retriever=bm25,
        vector_weight=0.7,
        bm25_weight=0.3,
    )

    results = retriever.search(
        "FastAPI deployment",
        top_k=2,
    )

    assert results
    assert results[0]["score"] >= results[-1]["score"]