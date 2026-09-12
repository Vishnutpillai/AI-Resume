import numpy as np

from src.embeddings.embedding_model import get_embedding_model
from src.embeddings.vector_store import VectorStore


def test_embedding_dimension():
    model = get_embedding_model()

    embeddings = model.encode(["Python machine learning"])

    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (1, 384)


def test_vector_store_add_and_search():
    model = get_embedding_model()

    documents = [
        "Python machine learning project",
        "Docker deployment",
        "SQL database development",
    ]

    embeddings = model.encode(documents)

    store = VectorStore(dimension=embeddings.shape[1])
    store.add(embeddings, documents)

    query_embedding = model.encode(
        ["machine learning with Python"]
    )[0]

    results = store.search(
        query_embedding,
        top_k=2,
    )

    assert len(results) == 2
    assert results[0]["document"] == "Python machine learning project"
    assert results[0]["score"] > results[1]["score"]


def test_vector_store_empty_search():
    store = VectorStore(dimension=384)

    query = np.zeros(384, dtype="float32")

    results = store.search(query, top_k=5)

    assert results == []


def test_vector_store_rejects_mismatched_documents():
    store = VectorStore(dimension=384)

    embeddings = np.zeros((2, 384), dtype="float32")
    documents = ["only one document"]

    try:
        store.add(embeddings, documents)
        assert False, "Expected ValueError"
    except ValueError:
        pass