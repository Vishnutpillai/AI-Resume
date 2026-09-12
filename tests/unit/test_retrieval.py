from src.retrieval.chunker import TextChunker, chunk_text
from src.retrieval.vector_index import PersistentVectorIndex


def test_chunker_splits_sections():
    text = (
        "SUMMARY\n"
        "Data Scientist with Python and SQL.\n\n"
        "PROJECTS\n"
        "Built machine learning models using Python, pandas and scikit-learn."
    )

    chunks = chunk_text(text)

    assert len(chunks) == 2
    assert chunks[0].source == "unknown"
    assert "SUMMARY" in chunks[0].text
    assert "PROJECTS" in chunks[1].text


def test_chunker_handles_empty_text():
    chunker = TextChunker()

    assert chunker.split_text("") == []
    assert chunker.split_text("   ") == []


def test_chunker_validates_overlap():
    try:
        TextChunker(chunk_size=100, overlap=100)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_chunker_splits_long_text():
    text = "Python machine learning " * 100

    chunks = chunk_text(
        text,
        source="resume",
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) > 1
    assert all(chunk.text for chunk in chunks)
    assert all(chunk.source == "resume" for chunk in chunks)


def test_persistent_vector_index_build_and_search():
    chunks = chunk_text(
        """
        SUMMARY
        Data Scientist with Python and machine learning experience.

        PROJECTS
        Built machine learning prediction systems using Python and scikit-learn.

        EXPERIENCE
        Worked with SQL databases and data analysis.
        """,
        source="resume",
        chunk_size=300,
        overlap=50,
    )

    index = PersistentVectorIndex()
    index.build(chunks)

    results = index.search(
        "Python machine learning project",
        top_k=2,
    )

    assert len(results) == 2
    assert results[0]["score"] >= results[1]["score"]