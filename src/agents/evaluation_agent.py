from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile

from src.evaluation.ats_analyzer import analyze_ats
from src.evaluation.skill_gap_analyzer import analyze_skill_gaps
from src.matching.scoring_engine import calculate_match_result
from src.retrieval.rag_pipeline import RAGPipeline


class EvaluationAgent:
    """
    Produce a unified evaluation of a resume against a job.

    The agent combines the existing deterministic:
        - match scoring
        - ATS analysis
        - skill-gap analysis

    LLM reasoning will be added later through the arbitration layer.
    """

    def __init__(self, rag_pipeline: RAGPipeline | None = None):
        self.rag_pipeline = rag_pipeline

    def evaluate(
        self,
        resume: ResumeProfile,
        job: JobProfile,
        resume_text: str,
        job_text: str,
    ) -> dict[str, object]:
        if not resume:
            raise ValueError("Resume profile is required.")

        if not job:
            raise ValueError("Job profile is required.")

        if not resume_text or not resume_text.strip():
            raise ValueError("Resume text is required.")

        if not job_text or not job_text.strip():
            raise ValueError("Job description text is required.")

        match_result = calculate_match_result(
            resume=resume,
            job=job,
            resume_text=resume_text,
            job_text=job_text,
        )

        ats_result = analyze_ats(
            resume=resume,
            job=job,
            resume_text=resume_text,
        )

        skill_gap_result = analyze_skill_gaps(
            resume=resume,
            job=job,
        )

        return {
            "candidate_id": resume.candidate_id,
            "job_id": job.job_id,
            "overall_match_score": match_result["overall_score"],
            "match_breakdown": match_result["breakdown"],
            "skill_match": match_result["skill_match"],
            "strengths": list(match_result["strengths"]),
            "weaknesses": list(match_result["weaknesses"]),
            "recommendations": list(match_result["recommendations"]),
            "ats_analysis": ats_result,
            "skill_gap_analysis": skill_gap_result,
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

    def evaluate_with_context(
        self,
        resume: ResumeProfile,
        job: JobProfile,
        resume_text: str,
        job_text: str,
        query: str,
        top_k: int = 5,
    ) -> dict[str, object]:
        evaluation = self.evaluate(
            resume=resume,
            job=job,
            resume_text=resume_text,
            job_text=job_text,
        )

        evaluation["evidence"] = self.retrieve_relevant_evidence(
            query=query,
            top_k=top_k,
        )

        return evaluation