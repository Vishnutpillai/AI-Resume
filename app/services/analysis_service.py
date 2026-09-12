from sqlalchemy.orm import Session

from app.models.entities import MatchRecord
from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile

from database.crud import create_match_result

from src.agents.orchestrator import AgentOrchestrator
from src.agents.llm_arbitrator import LLMArbitrator


class AnalysisService:
    """
    Application service responsible for running the complete
    deterministic analysis pipeline and optionally generating
    the final LLM explanation.
    """

    def __init__(
        self,
        orchestrator: AgentOrchestrator | None = None,
        arbitrator: LLMArbitrator | None = None,
    ):
        self.orchestrator = orchestrator or AgentOrchestrator()
        self.arbitrator = arbitrator or LLMArbitrator()

    def analyze(
        self,
        db: Session,
        resume: ResumeProfile,
        job: JobProfile,
        resume_text: str,
        job_text: str,
        use_llm: bool = True,
    ) -> dict[str, object]:
        deterministic_result = self.orchestrator.run(
            resume=resume,
            job=job,
            resume_text=resume_text,
            job_text=job_text,
        )

        matching_analysis = deterministic_result["matching_analysis"]

        match_record: MatchRecord = create_match_result(
            db=db,
            candidate_id=resume.candidate_id,
            job_id=job.job_id,
            overall_score=float(
                matching_analysis["overall_score"]
            ),
        )

        result: dict[str, object] = {
            "candidate_id": resume.candidate_id,
            "job_id": job.job_id,
            "deterministic_analysis": deterministic_result,
            "match_record_id": match_record.id,
        }

        if use_llm:
            arbitration_input = {
                "candidate_id": resume.candidate_id,
                "job_id": job.job_id,
                "overall_match_score": matching_analysis[
                    "overall_score"
                ],
                "strengths": matching_analysis["strengths"],
                "weaknesses": matching_analysis["weaknesses"],
                "skill_gaps": (
                    deterministic_result[
                        "skill_analysis"
                    ]["missing_required_skills"]
                ),
                "recommendations": matching_analysis[
                    "recommendations"
                ],
            }

            result["llm_analysis"] = self.arbitrator.arbitrate(
                arbitration_input
            )

        return result