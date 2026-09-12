from app.schemas.job import JobProfile
from app.schemas.resume import (
    Education,
    Experience,
    Project,
    ResumeProfile,
)

from src.agents.llm_arbitrator import LLMArbitrator
from src.agents.orchestrator import AgentOrchestrator
from src.retrieval.rag_pipeline import RAGPipeline


def sample_resume() -> ResumeProfile:
    return ResumeProfile(
        candidate_id="candidate_001",
        name="Test Candidate",
        summary="Data Scientist with Python and SQL experience.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "Pandas",
            "Docker",
        ],
        experience=[
            Experience(
                company="ABC Technologies",
                role="Data Scientist",
                years=1.5,
            )
        ],
        projects=[
            Project(
                name="Churn Prediction",
                description=(
                    "Built a machine learning prediction system "
                    "using Python, pandas and scikit-learn."
                ),
                technologies=[
                    "Python",
                    "Pandas",
                    "Scikit-learn",
                ],
            ),
            Project(
                name="ML Deployment",
                description=(
                    "Built an API for serving machine learning predictions."
                ),
                technologies=[
                    "FastAPI",
                    "Docker",
                ],
            ),
        ],
        education=[
            Education(
                degree="Bachelor's Degree",
                field="Computer Science",
                institution="Test University",
                year=2024,
            )
        ],
    )


def sample_job() -> JobProfile:
    return JobProfile(
        job_id="job_001",
        title="Data Scientist",
        company="ABC Technologies",
        description=(
            "Develop machine learning models and predictive solutions "
            "using Python and SQL. Experience deploying ML systems "
            "is preferred."
        ),
        required_skills=[
            "Python",
            "SQL",
            "Machine Learning",
            "Pandas",
        ],
        preferred_skills=[
            "Docker",
            "AWS",
            "FastAPI",
        ],
        minimum_experience=1.0,
        education="Bachelor's degree in Computer Science",
        keywords=[
            "Data Scientist",
            "Python",
            "SQL",
            "Machine Learning",
            "Predictive Modeling",
        ],
    )


def build_resume_text(resume: ResumeProfile) -> str:
    sections = [
        resume.summary or "",
        " ".join(resume.skills),
    ]

    for experience in resume.experience:
        sections.append(
            f"{experience.role} {experience.company or ''}"
        )

    for project in resume.projects:
        sections.append(
            f"{project.name} "
            f"{project.description or ''} "
            f"{' '.join(project.technologies)}"
        )

    return "\n".join(
        section for section in sections if section.strip()
    )


def build_job_text(job: JobProfile) -> str:
    return "\n".join(
        [
            job.title,
            job.description or "",
            "Required: " + ", ".join(job.required_skills),
            "Preferred: " + ", ".join(job.preferred_skills),
            "Keywords: " + ", ".join(job.keywords),
        ]
    )


def test_phase4_retrieval_pipeline():
    resume_text = (
        "Data Scientist Python SQL machine learning pandas. "
        "Built churn prediction using scikit-learn. "
        "Built ML API using FastAPI and Docker."
    )

    pipeline = RAGPipeline(
        chunk_size=300,
        overlap=50,
    )

    chunks = pipeline.build(
        resume_text,
        source="resume",
    )

    assert chunks

    result = pipeline.query(
        "Python machine learning deployment",
        retrieval_k=5,
        top_k=3,
    )

    assert result["results"]
    assert result["context"]


def test_phase4_orchestrator_pipeline():
    resume = sample_resume()
    job = sample_job()

    resume_text = build_resume_text(resume)
    job_text = build_job_text(job)

    orchestrator = AgentOrchestrator()

    result = orchestrator.run(
        resume=resume,
        job=job,
        resume_text=resume_text,
        job_text=job_text,
    )

    assert result["candidate_id"] == "candidate_001"
    assert result["job_id"] == "job_001"

    assert result["resume_analysis"]
    assert result["jd_analysis"]
    assert result["skill_analysis"]
    assert result["matching_analysis"]
    assert result["evaluation_analysis"]


def test_phase4_real_llm_arbitration():
    arbitrator = LLMArbitrator()

    analysis = {
        "candidate_id": "candidate_001",
        "job_id": "job_001",
        "overall_match_score": 82.5,
        "strengths": [
            "Python",
            "SQL",
            "Machine Learning",
        ],
        "weaknesses": [
            "AWS",
        ],
        "skill_gaps": [
            "AWS",
        ],
        "recommendations": [
            "Highlight relevant deployment experience.",
        ],
    }

    result = arbitrator.arbitrate(analysis)

    assert isinstance(result["summary"], str)
    assert result["summary"]

    assert isinstance(result["strengths"], list)
    assert isinstance(result["weaknesses"], list)
    assert isinstance(result["skill_gaps"], list)
    assert isinstance(result["recommendations"], list)


def test_phase4_complete_workflow():
    resume = sample_resume()
    job = sample_job()

    resume_text = build_resume_text(resume)
    job_text = build_job_text(job)

    orchestrator = AgentOrchestrator()

    deterministic_result = orchestrator.run(
        resume=resume,
        job=job,
        resume_text=resume_text,
        job_text=job_text,
    )

    arbitration_input = {
        "candidate_id": deterministic_result["candidate_id"],
        "job_id": deterministic_result["job_id"],
        "overall_match_score": (
            deterministic_result[
                "matching_analysis"
            ]["overall_score"]
        ),
        "strengths": deterministic_result[
            "matching_analysis"
        ]["strengths"],
        "weaknesses": deterministic_result[
            "matching_analysis"
        ]["weaknesses"],
        "skill_gaps": (
            deterministic_result[
                "skill_analysis"
            ]["missing_required_skills"]
        ),
        "recommendations": deterministic_result[
            "matching_analysis"
        ]["recommendations"],
    }

    arbitrator = LLMArbitrator()

    final_result = arbitrator.arbitrate(
        arbitration_input
    )

    assert deterministic_result["matching_analysis"][
        "overall_score"
    ] >= 0

    assert final_result["summary"]
    assert isinstance(final_result["strengths"], list)
    assert isinstance(final_result["weaknesses"], list)
    assert isinstance(final_result["skill_gaps"], list)
    assert isinstance(final_result["recommendations"], list)