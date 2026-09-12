from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile

from src.agents.evaluation_agent import EvaluationAgent
from src.agents.jd_agent import JDAgent
from src.agents.matching_agent import MatchingAgent
from src.agents.resume_agent import ResumeAgent
from src.agents.skill_agent import SkillAgent


class AgentOrchestrator:
    """
    Coordinate the specialized agents involved in resume-to-job
    analysis.

    The orchestrator is deterministic at this stage. LLM-based
    reasoning and arbitration are added in the next step.
    """

    def __init__(
        self,
        resume_agent: ResumeAgent | None = None,
        jd_agent: JDAgent | None = None,
        skill_agent: SkillAgent | None = None,
        matching_agent: MatchingAgent | None = None,
        evaluation_agent: EvaluationAgent | None = None,
    ):
        self.resume_agent = resume_agent or ResumeAgent()
        self.jd_agent = jd_agent or JDAgent()
        self.skill_agent = skill_agent or SkillAgent()
        self.matching_agent = matching_agent or MatchingAgent()
        self.evaluation_agent = evaluation_agent or EvaluationAgent()

    def run(
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

        resume_analysis = self.resume_agent.analyze(
            resume=resume,
        )

        jd_analysis = self.jd_agent.analyze(
            job=job,
        )

        skill_analysis = self.skill_agent.analyze(
            resume=resume,
            job=job,
        )

        matching_analysis = self.matching_agent.analyze(
            resume=resume,
            job=job,
            resume_text=resume_text,
            job_text=job_text,
        )

        evaluation_analysis = self.evaluation_agent.evaluate(
            resume=resume,
            job=job,
            resume_text=resume_text,
            job_text=job_text,
        )

        return {
            "candidate_id": resume.candidate_id,
            "job_id": job.job_id,
            "resume_analysis": resume_analysis,
            "jd_analysis": jd_analysis,
            "skill_analysis": skill_analysis,
            "matching_analysis": matching_analysis,
            "evaluation_analysis": evaluation_analysis,
        }