from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile
from src.evaluation.skill_gap_analyzer import analyze_skill_gaps
from src.matching.skill_matcher import match_skills, normalize_skill
from src.retrieval.rag_pipeline import RAGPipeline


class SkillAgent:
    """
    Analyze resume and job skills using the existing deterministic
    skill matching and skill-gap analysis components.
    """

    def __init__(self, rag_pipeline: RAGPipeline | None = None):
        self.rag_pipeline = rag_pipeline

    @staticmethod
    def _restore_skill_names(
        normalized_skills: list[str],
        source_skills: list[str],
    ) -> list[str]:
        """
        Convert normalized skill names back to the original display
        names from the source list.

        Example:
            normalized: ["python", "scikit-learn"]
            source: ["Python", "Scikit-learn"]

            returns:
            ["Python", "Scikit-learn"]
        """
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
    ) -> dict[str, object]:
        if not resume:
            raise ValueError("Resume profile is required.")

        if not job:
            raise ValueError("Job profile is required.")

        # Required skills are the primary skills used for matching.
        required_match = match_skills(
            resume_skills=resume.skills,
            job_skills=job.required_skills,
        )

        # Preferred skills are analyzed separately.
        preferred_match = match_skills(
            resume_skills=resume.skills,
            job_skills=job.preferred_skills,
        )

        skill_gaps = analyze_skill_gaps(
            resume=resume,
            job=job,
        )

        matched_required = self._restore_skill_names(
            normalized_skills=required_match["matched"],
            source_skills=resume.skills,
        )

        missing_required = self._restore_skill_names(
            normalized_skills=required_match["missing"],
            source_skills=job.required_skills,
        )

        matched_preferred = self._restore_skill_names(
            normalized_skills=preferred_match["matched"],
            source_skills=resume.skills,
        )

        missing_preferred = self._restore_skill_names(
            normalized_skills=preferred_match["missing"],
            source_skills=job.preferred_skills,
        )

        return {
            "candidate_id": resume.candidate_id,
            "job_id": job.job_id,
            "matched_required_skills": matched_required,
            "missing_required_skills": missing_required,
            "matched_preferred_skills": matched_preferred,
            "missing_preferred_skills": missing_preferred,
            "required_skill_score": required_match["score"],
            "preferred_skill_score": preferred_match["score"],
            "skill_gaps": skill_gaps,
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
        query: str,
        top_k: int = 5,
    ) -> dict[str, object]:
        analysis = self.analyze(
            resume=resume,
            job=job,
        )

        analysis["evidence"] = self.retrieve_relevant_evidence(
            query=query,
            top_k=top_k,
        )

        return analysis