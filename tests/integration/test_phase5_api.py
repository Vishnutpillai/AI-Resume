from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def sample_resume():
    return {
        "candidate_id": "integration_candidate",
        "name": "Integration Candidate",
        "summary": "Data Scientist with Python and SQL experience.",
        "skills": [
            "Python",
            "SQL",
            "Machine Learning",
            "Pandas",
        ],
        "experience": [
            {
                "company": "ABC Technologies",
                "role": "Data Scientist",
                "years": 1.5,
            }
        ],
        "projects": [
            {
                "name": "ML Prediction",
                "description": (
                    "Built a machine learning prediction system "
                    "using Python and scikit-learn."
                ),
                "technologies": [
                    "Python",
                    "Scikit-learn",
                ],
            }
        ],
        "education": [
            {
                "degree": "Bachelor's Degree",
                "field": "Computer Science",
                "institution": "Test University",
                "year": 2024,
            }
        ],
        "certifications": [],
    }


def sample_job():
    return {
        "job_id": "integration_job",
        "title": "Data Scientist",
        "company": "ABC Technologies",
        "description": (
            "Develop machine learning models and predictive "
            "solutions using Python and SQL."
        ),
        "required_skills": [
            "Python",
            "SQL",
            "Machine Learning",
        ],
        "preferred_skills": [
            "Docker",
            "AWS",
        ],
        "minimum_experience": 1.0,
        "education": "Bachelor's degree in Computer Science",
        "keywords": [
            "Data Scientist",
            "Python",
            "Machine Learning",
        ],
    }


def test_health_api():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_resume_api():
    response = client.post(
        "/api/v1/resume/analyze",
        json={
            "candidate_id": "integration_candidate",
            "name": "Integration Candidate",
            "summary": "Data Scientist",
            "skills": ["Python", "SQL"],
            "resume_text": "Python SQL Machine Learning",
        },
    )

    assert response.status_code == 200
    assert response.json()["candidate_id"] == (
        "integration_candidate"
    )


def test_job_api():
    response = client.post(
        "/api/v1/job/analyze",
        json={
            "job_id": "integration_job",
            "title": "Data Scientist",
            "company": "ABC Technologies",
            "description": "Build ML models.",
            "required_skills": ["Python", "SQL"],
            "preferred_skills": ["Docker"],
            "minimum_experience": 1.0,
            "education": "Bachelor's degree",
            "keywords": ["Machine Learning"],
            "job_text": "Python SQL Machine Learning",
        },
    )

    assert response.status_code == 200
    assert response.json()["job_id"] == "integration_job"


def test_analysis_api():
    response = client.post(
        "/api/v1/analysis",
        json={
            "resume": sample_resume(),
            "job": sample_job(),
            "resume_text": (
                "Data Scientist Python SQL Machine Learning "
                "Pandas scikit-learn"
            ),
            "job_text": (
                "Data Scientist Python SQL Machine Learning"
            ),
            "use_llm": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["candidate_id"] == (
        "integration_candidate"
    )
    assert data["job_id"] == "integration_job"
    assert data["match_record_id"] is not None
    assert (
        "deterministic_analysis"
        in data
    )


def test_optimization_api():
    response = client.post(
        "/api/v1/optimization",
        params={
            "resume_text": (
                "Data Scientist Python SQL "
                "Machine Learning Pandas"
            ),
            "job_text": (
                "Data Scientist Python SQL "
                "Machine Learning"
            ),
        },
        json={
            "resume": sample_resume(),
            "job": sample_job(),
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "initial_match" in data
    assert "optimized_match" in data
    assert "comparison" in data
    assert "optimization_accepted" in data
    assert "final_match" in data


def test_export_api():
    response = client.post(
        "/api/v1/export/docx",
        json=sample_resume(),
    )

    assert response.status_code == 200
    assert len(response.content) > 0

    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def test_recommendation_api():
    second_job = sample_job()

    second_job["job_id"] = "integration_job_2"
    second_job["title"] = "Python Developer"
    second_job["required_skills"] = ["Python"]

    response = client.post(
        "/api/v1/recommendations",
        json={
            "resume": sample_resume(),
            "resume_text": (
                "Data Scientist Python SQL "
                "Machine Learning"
            ),
            "jobs": [
                sample_job(),
                second_job,
            ],
            "job_texts": [
                "Data Scientist Python SQL Machine Learning",
                "Python Developer Python",
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["candidate_id"] == (
        "integration_candidate"
    )
    assert data["total_jobs"] == 2
    assert len(data["recommendations"]) == 2
    assert data["recommendations"][0]["rank"] == 1
    