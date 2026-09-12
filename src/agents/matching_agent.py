from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile
from src.matching.scoring_engine import calculate_match_result
from src.matching.skill_matcher import normalize_skill
from src.retrieval.rag_pipeline import RAGPipeline


class MatchingAgent:
    """
    Produce the overall resume-to-job match analysis using the
    existing deterministic scoring engine.
    """

    def __init__(self, rag_pipeline: RAGPipeline | None = None):
        self.rag_pipeline = rag_pipeline

    @staticmethod
    def _restore_skill_names(
        normalized_skills: list[str],
        source_skills: list[str],
    ) -> list[str]:
        source_map: dict[str, str] = {}

        for skill in source_skills:
            if not skill or not skill.strip():
                continue

            normalized = normalize_skill(skill)

            if normalized and normalized not in source_map:
                source_map[normalized] = skill.strip()

        return [
            source_map.get(skill, skill)
            for skill in normalized_skills
        ]

    def analyze(
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

        breakdown = match_result["breakdown"]
        skill_match = match_result["skill_match"]

        if hasattr(breakdown, "model_dump"):
            breakdown = breakdown.model_dump()

        if hasattr(skill_match, "model_dump"):
            skill_match = skill_match.model_dump()

        if isinstance(skill_match, dict):
            skill_match = {
                **skill_match,
                "matched": self._restore_skill_names(
                    normalized_skills=skill_match.get("matched", []),
                    source_skills=resume.skills,
                ),
                "missing": self._restore_skill_names(
                    normalized_skills=skill_match.get("missing", []),
                    source_skills=job.required_skills,
                ),
            }

        return {
            "candidate_id": resume.candidate_id,
            "job_id": job.job_id,
            "overall_score": match_result["overall_score"],
            "breakdown": breakdown,
            "skill_match": skill_match,
            "strengths": list(match_result["strengths"]),
            "weaknesses": list(match_result["weaknesses"]),
            "recommendations": list(match_result["recommendations"]),
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
        resume: ResumeProfile,
        job: JobProfile,
        resume_text: str,
        job_text: str,
        query: str,
        top_k: int = 5,
    ) -> dict[str, object]:
        analysis = self.analyze(
            resume=resume,
            job=job,
            resume_text=resume_text,
            job_text=job_text,
        )

        analysis["evidence"] = self.retrieve_relevant_evidence(
            query=query,
            top_k=top_k,
        )

        return analysis