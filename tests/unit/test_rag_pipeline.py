from src.retrieval.rag_pipeline import RAGPipeline


def test_rag_pipeline_build():
    pipeline = RAGPipeline(
        chunk_size=200,
        overlap=20,
    )

    chunks = pipeline.build(
        """
        SUMMARY
        Data Scientist with Python and machine learning experience.

        PROJECTS
        Built machine learning models using Python and scikit-learn.

        EXPERIENCE
        Worked with SQL databases and Docker deployment.
        """,
        source="resume",
    )

    assert chunks
    assert pipeline.hybrid_retriever is not None


def test_rag_pipeline_query():
    pipeline = RAGPipeline(
        chunk_size=300,
        overlap=30,
    )

    pipeline.build(
        """
        PROJECT
        Built a machine learning prediction system using Python,
        pandas and scikit-learn.

        DEPLOYMENT
        Deployed applications using Docker and FastAPI.

        DATABASE
        Worked with SQL database analytics.
        """,
        source="resume",
    )

    result = pipeline.query(
        "Python machine learning project",
        retrieval_k=3,
        top_k=2,
    )

    assert result["query"] == "Python machine learning project"
    assert len(result["results"]) <= 2
    assert result["context"]


def test_rag_pipeline_empty_query():
    pipeline = RAGPipeline()

    pipeline.build(
        "Python machine learning project",
        source="resume",
    )

    result = pipeline.query("")

    assert result["results"] == []
    assert result["context"] == ""


def test_rag_pipeline_build_requires_text():
    pipeline = RAGPipeline()

    try:
        pipeline.build("")
        assert False, "Expected ValueError"
    except ValueError:
        pass