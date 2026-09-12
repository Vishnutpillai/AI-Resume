from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_job_recommendation_endpoint():
    payload = {
        "resume": {
            "candidate_id": "candidate_001",
            "name": "Test Candidate",
            "summary": "Data Scientist with Python experience.",
            "skills": [
                "Python",
                "SQL",
                "Machine Learning",
            ],
            "experience": [],
            "projects": [],
            "education": [],
            "certifications": [],
        },
        "resume_text": (
            "Data Scientist Python SQL Machine Learning"
        ),
        "jobs": [
            {
                "job_id": "job_001",
                "title": "Data Scientist",
                "company": "Company A",
                "description": (
                    "Build machine learning models."
                ),
                "required_skills": [
                    "Python",
                    "SQL",
                    "Machine Learning",
                ],
                "preferred_skills": [],
                "minimum_experience": 0,
                "education": None,
                "keywords": [],
            },
            {
                "job_id": "job_002",
                "title": "Excel Analyst",
                "company": "Company B",
                "description": (
                    "Create reports using Excel."
                ),
                "required_skills": [
                    "Excel",
                ],
                "preferred_skills": [],
                "minimum_experience": 0,
                "education": None,
                "keywords": [],
            },
        ],
        "job_texts": [
            "Data Scientist Python SQL Machine Learning",
            "Excel Analyst reporting",
        ],
    }

    response = client.post(
        "/api/v1/recommendations",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["candidate_id"] == "candidate_001"
    assert data["total_jobs"] == 2
    assert len(data["recommendations"]) == 2
    assert data["recommendations"][0]["rank"] == 1