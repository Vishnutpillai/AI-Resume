from app.schemas.job import JobProfile
from app.schemas.resume import ResumeProfile
from app.services.job_recommendation_service import (
    JobRecommendationService,
)


def sample_resume():
    return ResumeProfile(
        candidate_id="candidate_001",
        name="Test Candidate",
        summary="Data Scientist with Python and SQL experience.",
        skills=[
            "Python",
            "SQL",
            "Machine Learning",
        ],
        experience=[],
        projects=[],
        education=[],
        certifications=[],
    )


def test_job_recommendation_ranking():
    service = JobRecommendationService()

    jobs = [
        JobProfile(
            job_id="job_001",
            title="Data Analyst",
            company="Company A",
            description="Work with Excel and reporting.",
            required_skills=["Excel"],
        ),
        JobProfile(
            job_id="job_002",
            title="Data Scientist",
            company="Company B",
            description="Build machine learning models.",
            required_skills=[
                "Python",
                "SQL",
                "Machine Learning",
            ],
        ),
        JobProfile(
            job_id="job_003",
            title="Python Developer",
            company="Company C",
            description="Develop Python applications.",
            required_skills=["Python"],
        ),
    ]

    job_texts = [
        "Data Analyst Excel reporting",
        "Data Scientist Python SQL Machine Learning",
        "Python Developer Python applications",
    ]

    results = service.recommend(
        resume=sample_resume(),
        resume_text=(
            "Data Scientist Python SQL Machine Learning"
        ),
        jobs=jobs,
        job_texts=job_texts,
    )

    assert len(results) == 3
    assert results[0]["rank"] == 1
    assert results[0]["job_id"] == "job_002"

    assert (
        results[0]["overall_score"]
        >= results[1]["overall_score"]
    )


def test_empty_jobs():
    service = JobRecommendationService()

    results = service.recommend(
        resume=sample_resume(),
        resume_text="Python SQL Machine Learning",
        jobs=[],
        job_texts=[],
    )

    assert results == []


def test_mismatched_job_inputs():
    service = JobRecommendationService()

    jobs = [
        JobProfile(
            job_id="job_001",
            title="Data Scientist",
        )
    ]

    try:
        service.recommend(
            resume=sample_resume(),
            resume_text="Python",
            jobs=jobs,
            job_texts=[],
        )
        assert False, "Expected ValueError"
    except ValueError:
        pass