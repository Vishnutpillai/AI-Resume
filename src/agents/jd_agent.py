from app.schemas.job import JobProfile
from src.retrieval.rag_pipeline import RAGPipeline


class JDAgent:
    """
    Analyze job description information and prepare structured
    evidence for downstream matching and evaluation agents.

    The agent is deterministic at this stage. LLM reasoning is
    added later through the arbitration layer.
    """

    def __init__(self, rag_pipeline: RAGPipeline | None = None):
        self.rag_pipeline = rag_pipeline

    def analyze(self, job: JobProfile) -> dict[str, object]:
        if not job:
            raise ValueError("Job profile is required.")

        required_skills = [
            skill.strip()
            for skill in job.required_skills
            if skill and skill.strip()
        ]

        preferred_skills = [
            skill.strip()
            for skill in job.preferred_skills
            if skill and skill.strip()
        ]

        keywords = [
            keyword.strip()
            for keyword in job.keywords
            if keyword and keyword.strip()
        ]

        return {
            "job_id": job.job_id,
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "minimum_experience": job.minimum_experience,
            "education": job.education,
            "keywords": keywords,
        }

    def retrieve_relevant_evidence(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, object]]:
        if self.rag_pipeline is None:
            raise RuntimeError(
                "RAG pipeline is required for evidence retrieval."
            )

        return self.rag_pipeline.retrieve(
            query=query,
            top_k=top_k,
        )

    def analyze_with_context(
        self,
        job: JobProfile,
        query: str,
        top_k: int = 5,
    ) -> dict[str, object]:
        analysis = self.analyze(job)

        evidence = self.retrieve_relevant_evidence(
            query=query,
            top_k=top_k,
        )

        analysis["evidence"] = evidence

        return analysis