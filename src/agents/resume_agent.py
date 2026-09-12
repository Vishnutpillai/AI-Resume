from app.schemas.resume import ResumeProfile
from src.retrieval.rag_pipeline import RAGPipeline


class ResumeAgent:
    """
    Analyze resume information and prepare structured evidence
    for downstream matching and evaluation agents.

    The agent is deliberately deterministic at this stage.
    LLM reasoning will be added through the arbitration layer later.
    """

    def __init__(self, rag_pipeline: RAGPipeline | None = None):
        self.rag_pipeline = rag_pipeline

    def analyze(self, resume: ResumeProfile) -> dict[str, object]:
        if not resume:
            raise ValueError("Resume profile is required.")

        skills = [
            skill.strip()
            for skill in resume.skills
            if skill and skill.strip()
        ]

        experience = [
            {
                "company": item.company,
                "role": item.role,
                "years": item.years,
            }
            for item in resume.experience
        ]

        projects = [
            {
                "name": project.name,
                "description": project.description,
                "technologies": project.technologies,
            }
            for project in resume.projects
        ]

        education = [
            {
                "degree": item.degree,
                "field": item.field,
                "institution": item.institution,
                "year": item.year,
            }
            for item in resume.education
        ]

        return {
            "candidate_id": resume.candidate_id,
            "name": resume.name,
            "summary": resume.summary,
            "skills": skills,
            "experience": experience,
            "projects": projects,
            "education": education,
            "certifications": list(resume.certifications),
            "total_experience_years": sum(
                item.years for item in resume.experience
            ),
            "project_count": len(resume.projects),
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
        query: str,
        top_k: int = 5,
    ) -> dict[str, object]:
        analysis = self.analyze(resume)

        evidence = self.retrieve_relevant_evidence(
            query=query,
            top_k=top_k,
        )

        analysis["evidence"] = evidence
        return analysis