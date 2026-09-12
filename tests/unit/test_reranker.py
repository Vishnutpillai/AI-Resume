from src.reranking.reranker import get_reranker


def test_reranker_returns_ranked_results():
    reranker = get_reranker()

    results = [
        {
            "document": "Docker deployment using containers",
            "score": 0.4,
            "index": 1,
        },
        {
            "document": "Python machine learning with scikit-learn",
            "score": 0.8,
            "index": 0,
        },
    ]

    output = reranker.rerank(
        query="Python machine learning",
        results=results,
        top_k=2,
    )

    assert len(output) == 2
    assert "reranker_score" in output[0]
    assert output[0]["reranker_score"] >= output[1]["reranker_score"]


def test_reranker_empty_query():
    reranker = get_reranker()

    results = [
        {
            "document": "Python machine learning",
            "score": 1.0,
            "index": 0,
        }
    ]

    assert reranker.rerank("", results) == []


def test_reranker_empty_results():
    reranker = get_reranker()

    assert reranker.rerank(
        "Python machine learning",
        [],
    ) == []


def test_reranker_top_k():
    reranker = get_reranker()

    results = [
        {
            "document": "Python machine learning project",
            "score": 1.0,
            "index": 0,
        },
        {
            "document": "Docker deployment",
            "score": 0.8,
            "index": 1,
        },
        {
            "document": "SQL database",
            "score": 0.7,
            "index": 2,
        },
    ]

    output = reranker.rerank(
        query="Python machine learning",
        results=results,
        top_k=2,
    )

    assert len(output) == 2