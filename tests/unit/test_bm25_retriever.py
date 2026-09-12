from src.retrieval.bm25_retriever import BM25Retriever


def test_bm25_build_and_search():
    documents = [
        "Python machine learning project",
        "Docker deployment pipeline",
        "SQL database development",
    ]

    retriever = BM25Retriever(documents)

    results = retriever.search(
        "Python machine learning",
        top_k=2,
    )

    assert len(results) == 2
    assert results[0]["document"] == "Python machine learning project"
    assert results[0]["score"] >= results[1]["score"]


def test_bm25_case_insensitive():
    documents = [
        "Python Machine Learning",
        "SQL Database",
    ]

    retriever = BM25Retriever(documents)

    results = retriever.search(
        "python machine learning",
        top_k=1,
    )

    assert results[0]["document"] == "Python Machine Learning"


def test_bm25_empty_query():
    documents = [
        "Python machine learning",
        "Docker deployment",
    ]

    retriever = BM25Retriever(documents)

    assert retriever.search("", top_k=5) == []


def test_bm25_invalid_build():
    retriever = BM25Retriever()

    try:
        retriever.build([])
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_bm25_search_before_build():
    retriever = BM25Retriever()

    try:
        retriever.search("Python")
        assert False, "Expected RuntimeError"
    except RuntimeError:
        pass
    